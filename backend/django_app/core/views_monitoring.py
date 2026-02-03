from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings as django_settings
from django.utils import timezone
import asyncio
import os
import sys

# Add parent dir to path to import 'aeo' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from aeo.config import Settings
from aeo.output_monitoring.engines import (
    create_openai_engine, 
    create_anthropic_engine, 
    create_gemini_engine,
    query_multiple_engines
)
from aeo.output_monitoring.base import QueryResult
from aeo.output_monitoring.analysis.brand_analyzer import analyze_brand
from aeo.output_monitoring.query_generator import generate_sota_queries
from aeo.output_monitoring.analysis.insight_aggregator import aggregate_sota_insights
from aeo.output_monitoring.analysis.models import BrandProfile

from .utils import MockEngine
from .signals import llm_request_executed

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def analyze_brand_view(request):
    """
    Analyzes page content to extract brand profile and generate SOTA queries.
    """
    target_url = request.data.get('target_url')
    # Use provided page_content or fallback to scraping
    page_content = request.data.get('page_content', "")

    if not target_url:
        return Response({'error': 'target_url required'}, status=400)

    settings = Settings()
    if not settings.openai_api_key:
        return Response({'error': 'OpenAI API key missing'}, status=400)

    # Fallback: Fetch content if missing or too short
    if not page_content or len(page_content) < 100:
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Simple sync fetch for MVP speed (requests)
            resp = requests.get(target_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.extract()
                page_content = soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Fallback fetch failed: {e}")

    try:
        # Check if product_id is provided to use persistence
        product_id = request.data.get('product_id')
        product = None
        if product_id:
            from .models import Product
            product = Product.objects.filter(pk=product_id).first()
            
            # Return persisted if available
            if product and product.suggested_queries:
                return Response({
                    'profile': {'brand_name': product.name, 'business_bio': product.business_bio}, # approximation if we don't store full profile
                    'suggested_queries': product.suggested_queries
                })

        # Run brand analysis (async)
        profile = asyncio.run(analyze_brand(page_content, settings.openai_api_key))

        if not profile:
            # Instead of 500, return a gentle 422 or empty structure
            return Response({'error': 'Evidence insufficient for brand analysis'}, status=422)

        # Generate strategic queries
        queries = generate_sota_queries(profile)
        
        # Save if product context exists
        if product:
             product.suggested_queries = queries
             if not product.business_bio:
                 product.business_bio = profile.business_bio
             product.save()

        return Response({
            'profile': profile.dict(),
            'suggested_queries': queries
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh_queries(request):
    """
    Force re-generation of strategic queries.
    """
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'product_id required'}, status=400)
        
    from .models import Product
    product = get_object_or_404(Product, pk=product_id)
    
    # We need a profile to generate queries.
    # If we have bio, we can try to reconstruct a minimal profile or generate from bio.
    # `generate_sota_queries` takes a BrandProfile object.
    
    if not product.business_bio:
         return Response({'error': 'No bio available to generate queries'}, status=400)
         
    try:
        # Create a temporary profile from stored data
        # We might need to generate it if we want it fresh, but let's use what we have to save cost/time if possible?
        # User said "refreshable when we want to UPDATE them". This implies re-running AI.
        
        # We don't have the original page content here easily unless we rescraped.
        # But we surely have the bio. 
        # Let's use the Bio to generate a profile or Queries directly?
        # `generate_sota_queries` needs `BrandProfile`.
        # Let's mock a profile with the bio.
        
        from aeo.output_monitoring.analysis.models import BrandProfile
        # We might be missing fields, but let's try
        profile = BrandProfile(
            brand_name=product.name,
            business_bio=product.business_bio,
            key_offerings=[],
            target_audience=product.target_audience_age,
            unique_selling_points=[]
        )
        
        # Generate
        queries = generate_sota_queries(profile)
        
        # Logic to append or replace? "update them" -> usually replace for queries list?
        # "loaded everytime... persistent... refreshable... update them".
        # I'll replace them for now, or maybe append if user wants history?
        # Strategic questions usually change if context changes. List might get too long.
        # I will REPLACE.
        
        product.suggested_queries = queries
        product.save()
        
        return Response({'suggested_queries': queries})

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def output_query(request):
    """
    Run query against multiple AI engines.
    """
    query = request.data.get('query')
    target_url = request.data.get('target_url')
    engines_requested = request.data.get('engines', ['openai', 'anthropic', 'gemini'])
    product_id = request.data.get('product_id')
    
    if not query or not target_url:
        return Response({'error': 'query and target_url required'}, status=400)

    engines = []
    
    settings = Settings()
    
    # Check Feature Flag first
    if getattr(django_settings, 'USE_MOCK_LLM', False):
        print("Feature Flag USE_MOCK_LLM is True. Using Mock Engines.")
        engines.append(MockEngine("mock-openai"))
        engines.append(MockEngine("mock-anthropic"))
    else:
        # Standard Engine Loading
        if 'openai' in engines_requested and settings.openai_api_key:
            engines.append(create_openai_engine(settings.openai_api_key))
        if 'anthropic' in engines_requested and settings.anthropic_api_key:
            engines.append(create_anthropic_engine(settings.anthropic_api_key))
        if 'gemini' in engines_requested and settings.gemini_api_key:
            engines.append(create_gemini_engine(settings.gemini_api_key))
            
    if not engines:
        # Fallback to Mock Engine if no keys are present
        print("Warning: No API keys found. Using Mock Engines.")
        engines.append(MockEngine("mock-openai"))
        engines.append(MockEngine("mock-anthropic"))
        
    if not engines:
         return Response({'error': 'No valid engines available/configured'}, status=400)

    # Run queries
    try:
        results = asyncio.run(query_multiple_engines(query, target_url, engines))
    except Exception as e:
        return Response({'error': f'Async execution failed: {str(e)}'}, status=500)
    
    # Format Response
    formatted_results = []
    total_cost = 0.0
    cited_count = 0
    
    for r in results:
        if isinstance(r, QueryResult):
            formatted_results.append({
                'engine': r.engine,
                'response': r.response,
                'citations': [c.dict() for c in r.citations],
                'cost_usd': r.cost_usd,
                'latency_ms': r.latency_ms,
                'tokens_used': r.tokens_used
            })
            total_cost += r.cost_usd
            if r.citations:
                cited_count += 1
                
            # Run Advanced Analysis (if successful response)
            analysis = {}
            if r.response:
                try:
                    # We need to run this synchronously here since we are inside a sync view (mostly)
                    # or strictly speaking, we are in an async loop context if we are running query_multiple_engines
                    # But `analyze_response_metrics` is async.
                    # We are in `output_query` which handles `asyncio.run`.
                    # To effectively run this, we can't easily nest asyncio.run.
                    # We should probably run this AFTER the main gathering if we want parallelism,
                    # OR we just run it as a separate task?
                    # For MVP, let's just run it. We are already inside `asyncio.run` wrapper? 
                    # No, `output_query` calls `asyncio.run(query_multiple_engines...)`. 
                    # So we receive results back in sync context.
                    # We need to run another asyncio loop or run it sync.
                    
                    from aeo.output_monitoring.analysis import analyze_response_metrics
                    
                    # We need the product bio. It might be in request data or we need to fetch product.
                    # For now, let's try to get it from context or request.
                    # User request: "Executive Summary, now that we know more about the prodicut"
                    # We should fetch the product if possible.
                    # The `target_url` is passed. Maybe we can find product by domain?
                    # Or we just rely on what we have.
                    
                    brand_name = "the brand"
                    product_bio = ""
                    
                    # Try to find product by ID first, then domain
                    from .models import Product
                    product_obj = None
                    if product_id:
                         product_obj = Product.objects.filter(pk=product_id).first()
                    
                    if not product_obj:
                        # Simple domain check
                        parsed_domain = target_url.replace('https://', '').replace('http://', '').split('/')[0]
                        product_obj = Product.objects.filter(domain__icontains=parsed_domain).first()
                    
                    if product_obj:
                        brand_name = product_obj.name
                        product_bio = product_obj.business_bio
                    
                    # Create new loop for analysis
                    analysis_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(analysis_loop)
                    analysis = analysis_loop.run_until_complete(
                        analyze_response_metrics(
                            query=query,
                            response_text=r.response,
                            brand_name=brand_name,
                            product_bio=product_bio
                        )
                    )
                    analysis_loop.close()
                    
                except Exception as e:
                    print(f"Analysis failed: {e}")

            # EMIT SIGNAL for detailed logging (Single Table)
            llm_request_executed.send(
                sender=None, 
                interaction_data={
                    'target_url': target_url,
                    'query_text': query,
                    'engine': r.engine,
                    'prompt_text': query,
                    'response_text': r.response,
                    'tokens_input': 0,
                    'tokens_output': r.tokens_used, 
                    'cost_usd': r.cost_usd,
                    'latency_ms': r.latency_ms,
                    'success': True,
                    'metadata': {'target_url': target_url},
                    'analysis_data': analysis,
                    'product_id': product_id # Pass explicitly
                }
            )
            
    citation_rate = cited_count / len(formatted_results) if formatted_results else 0
    
    # SOTA Insights Aggregation
    sota_insights = {}
    brand_profile_data = request.data.get('brand_profile')
    if brand_profile_data and formatted_results:
        try:
            profile = BrandProfile(**brand_profile_data)
            sota_insights = aggregate_sota_insights(formatted_results, profile)
        except Exception as e:
            print(f"Insight aggregation failed: {e}")

    return Response({
        'query': query,
        'results': formatted_results,
        'total_cost_usd': round(total_cost, 4),
        'citation_rate': round(citation_rate, 2),
        'sota_insights': sota_insights
    })

@api_view(['GET'])
def available_engines(request):
    """
    Return list of configured/available engines.
    """
    settings = Settings()
    engines = []
    
    # Check OpenAI
    if settings.openai_api_key:
        engines.append({
            'id': 'openai',
            'name': 'OpenAI GPT-4o',
            'provider': 'openai',
            'model': 'gpt-4o-mini' 
        })
        
    # Check Anthropic
    if settings.anthropic_api_key:
        engines.append({
            'id': 'anthropic',
            'name': 'Claude Sonnet',
            'provider': 'anthropic',
            'model': 'claude-3-5-haiku-latest'
        })
        
    # Check Gemini
    if settings.gemini_api_key:
        engines.append({
            'id': 'gemini',
            'name': 'Gemini Flash',
            'provider': 'gemini',
            'model': 'gemini-2.0-flash-lite'
        })
        
    # If Mock LLM is enabled, always return standard list
    if getattr(django_settings, 'USE_MOCK_LLM', False):
        return Response([
            {'id': 'openai', 'name': 'Mock OpenAI', 'provider': 'mock'},
            {'id': 'anthropic', 'name': 'Mock Claude', 'provider': 'mock'},
            {'id': 'gemini', 'name': 'Mock Gemini', 'provider': 'mock'},
        ])
        
    return Response(engines)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_budget(request):
    """
    Return current spending/budget status.
    Calculates total cost from LLMInteraction logs.
    """
    from django.db.models import Sum
    from .models import LLMInteraction
    
    total_spend = LLMInteraction.objects.aggregate(total=Sum('cost_usd'))['total'] or 0.0
    
    # Hardcoded limit for now, or fetch from settings
    budget_limit = 10.0 
    
    return Response({
        'total_spend': round(total_spend, 4),
        'budget_limit': budget_limit,
        'remaining': round(max(0, budget_limit - total_spend), 4),
        'currency': 'USD'
    })

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_query_history(request):
    """
    Get list of unique past queries.
    Group by query_text and return latest timestamp.
    Accepts product_id to filter.
    """
    from .models import LLMInteraction
    from django.db.models import Max, Count, F, Q
    
    product_id = request.query_params.get('product_id')
    
    queryset = LLMInteraction.objects.all()
    if product_id:
        queryset = queryset.filter(product_id=product_id)
    
    # Simple grouping by query_text
    # We want: query_text, last_run, engine_count
    
    # 1. Get unique queries with annotation
    history = queryset.values('query_text').annotate(
        last_run=Max('timestamp'),
        engine_count=Count('id'),
        citation_count=Count('id', filter=Q(response_text__icontains='http')) # Rough proxy for citations if we don't have json field easily accessible in values()
    ).order_by('-last_run')[:20] 
    
    return Response(history)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_history_details(request):
    """
    Get full results for a specific query string.
    """
    query_text = request.query_params.get('query')
    if not query_text:
        return Response({'error': 'Query required'}, status=400)
        
    from .models import LLMInteraction
    
    latest = LLMInteraction.objects.filter(query_text=query_text).order_by('-timestamp').first()
    if not latest:
        return Response({'error': 'Not found'}, status=404)
        
    # Get all interactions for this query that happened within 5 seconds of the last one (grouping by time window)
    interactions = LLMInteraction.objects.filter(
        query_text=query_text,
        timestamp__gte=latest.timestamp - timezone.timedelta(seconds=10),
        timestamp__lte=latest.timestamp + timezone.timedelta(seconds=10)
    )
    
    formatted_results = []
    total_cost = 0.0
    cited_count = 0
    
    for r in interactions:
        import re
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', r.response_text or "")
        
        citations = [{'url': u, 'snippet': ''} for u in urls]
        
        formatted_results.append({
            'engine': r.engine,
            'response': r.response_text,
            'citations': citations,
            'cost_usd': float(r.cost_usd),
            'latency_ms': 0, 
            'tokens_used': 0 
        })
        total_cost += float(r.cost_usd)
        if citations:
            cited_count += 1
            
    citation_rate = cited_count / len(formatted_results) if formatted_results else 0
    
    return Response({
        'query': query_text,
        'results': formatted_results,
        'total_cost_usd': round(total_cost, 4),
        'citation_rate': round(citation_rate, 2)
    })


@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_history(request):
    """
    Delete all interactions for a specific query string.
    """
    query_text = request.query_params.get('query')
    if not query_text:
        return Response({'error': 'Query required'}, status=400)
    
    from .models import LLMInteraction
    
    deleted_count, _ = LLMInteraction.objects.filter(query_text=query_text).delete()
    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_similar_companies(request):
    """
    Get top 5 similar companies.
    Reads from DB or generates if missing.
    """
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({'error': 'product_id required'}, status=400)
        
    from .models import Product
    product = get_object_or_404(Product, pk=product_id)
    
    # Return persisted if available (and not empty)
    if product.competitors and len(product.competitors) > 0:
        return Response({'companies': product.competitors})
    
    # Generate on the fly if missing (and save)
    try:
        from .views_auth import generate_competitors, generate_bio
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 1. Auto-generate BIO if missing
        if not product.business_bio:
            print(f"Auto-generating bio for {product.name}...")
            product.business_bio = loop.run_until_complete(
                generate_bio(product.domain, product.name)
            )
            product.save() # Save bio immediately
            
        # 2. Generate Competitors
        if product.business_bio:
            competitors = loop.run_until_complete(
                generate_competitors(
                    product.business_bio,
                    product.target_region,
                    product.target_audience_age,
                    product.gender_preference
                )
            )
            
            if competitors:
                product.competitors = competitors
                product.save()
                return Response({'companies': competitors})
        
        # If still no bio or competitors failed
        return Response({'error': 'Could not generate analysis (missing bio or AI error)'}, status=500)
        
    except Exception as e:
        print(f"Competitor fetch failed: {e}")
        return Response({'error': str(e)}, status=500)
    finally:
        try:
            loop.close()
        except:
            pass

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh_competitors(request):
    """
    Force re-calculation of competitors and append to list.
    """
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'product_id required'}, status=400)
    
    from .models import Product
    from .views_auth import generate_competitors
    
    product = get_object_or_404(Product, pk=product_id)
    
    if not product.business_bio:
        return Response({'error': 'Product has no bio configured'}, status=400)
        
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        min_new_competitors = loop.run_until_complete(
            generate_competitors(
                product.business_bio,
                product.target_region,
                product.target_audience_age,
                product.gender_preference
            )
        )
        loop.close()
        
        if min_new_competitors:
            # Append to existing list
            # We might want to deduplicate via domain if needed, but user asked to "append"
            # Let's dedupe slightly to avoid exact dupes in the same run, but keep history if valuable.
            # "use the latest available from the unit" implies we prioritize new ones.
            # We'll just append them.
            
            # Ensure it's a list
            current_list = product.competitors if isinstance(product.competitors, list) else []
            
            # Make sure we don't just grow infinitely with exact duplicates
            # Let's verify duplication strategy. 
            # "update the database. Don't delete the old one. Append this"
            # Simple append:
            updated_list = min_new_competitors + current_list
            
            product.competitors = updated_list
            product.save()
            
            return Response({'companies': updated_list})
        else:
            return Response({'error': 'AI returned no competitors'}, status=500)
            
    except Exception as e:
        print(f"Refresh failed: {e}")
        return Response({'error': str(e)}, status=500)
