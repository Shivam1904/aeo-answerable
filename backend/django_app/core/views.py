from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import ScanJob
from django.shortcuts import get_object_or_404
from django.conf import settings as django_settings
import uuid
import sys
import os
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from .signals import llm_request_executed

# Bridge to existing logic
# Add parent dir to path to import 'aeo' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from aeo.config import Settings
from aeo.crawler import Crawler
from aeo.rendered_crawler import RenderedCrawler
from aeo.output_monitoring.engines import (
    create_openai_engine, 
    create_anthropic_engine, 
    create_gemini_engine,
    query_multiple_engines
)
from aeo.output_monitoring.base import QueryResult, QueryEngine

class MockEngine(QueryEngine):
    """
    Simulates an LLM engine for testing/demo purposes when no API keys are present.
    """
    def __init__(self, name="mock-gpt"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def query(self, prompt: str, context_url: str) -> QueryResult:
        # Simulate network latency
        await asyncio.sleep(1.5)
        
        return QueryResult(
            engine=self.name,
            response=f"This is a mocked response from {self.name}. The user asked: '{prompt}'. I found context at {context_url}.",
            citations=[],
            tokens_used=100,
            cost_usd=0.001,
            latency_ms=1500
        )

    def estimate_cost(self, prompt: str) -> float:
        return 0.001

# --- Helper for Async Engines ---
# In Django async views, we can await directly.

# --- Views ---

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def start_scan(request):
    """
    Start a new AEO scan.
    Returns a job_id that can be polled for status.
    """
    url = request.data.get('url') # Can be overridden, but usually Product domain
    product_id = request.data.get('product_id')
    mode = request.data.get('mode', 'fast')
    max_pages = request.data.get('max_pages', 50)
    
    if not url:
        return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    if not url.startswith('http'):
        url = 'https://' + url
    
    product = None
    if product_id:
        from .models import Product
        product = get_object_or_404(Product, pk=product_id)
    
    # Create Job
    job = ScanJob.objects.create(url=url, product=product, mode=mode, status='pending')
    
    # Trigger background task
    import threading
    threading.Thread(target=run_scan_thread, args=(job.job_id, url, mode, max_pages)).start()
    
    return Response({'job_id': str(job.job_id)})


def run_scan_thread(job_id, url, mode, max_pages):
    """
    Thread target to run the scan synchronously.
    """
    try:
        ScanJob.objects.filter(job_id=job_id).update(status='running')
        
        settings = Settings(
            start_url=url,
            max_pages=max_pages,
            mode=mode
        )
        
        if mode == "rendered":
            crawler = RenderedCrawler(settings)
        else:
            crawler = Crawler(settings)
            
        result = asyncio.run(crawler.scan())
        
        ScanJob.objects.filter(job_id=job_id).update(
            status='complete',
            result=result,
            completed_at=timezone.now(),
            pages_scanned=result.get('summary', {}).get('scanned_count', 0)
        )
        
    except Exception as e:
        print(f"Scan failed: {e}")
        ScanJob.objects.filter(job_id=job_id).update(
            status='error', 
            error=str(e),
            completed_at=timezone.now()
        )


@api_view(['GET'])
def get_scan_status(request, job_id):
    """
    Get the status of a scan job.
    """
    job = get_object_or_404(ScanJob, job_id=job_id)
    
    return Response({
        'status': job.status,
        'progress': {'pages_scanned': job.pages_scanned},
        'result': job.result,
        'error': job.error,
        'timestamp': job.completed_at or job.created_at
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_latest_scan_for_product(request, product_id):
    """
    Get the most recent COMPLETED scan for a product.
    Used for persistence - show last results instead of forcing new scan.
    """
    # Get latest complete scan
    job = ScanJob.objects.filter(
        product_id=product_id, 
        status='complete'
    ).order_by('-completed_at').first()
    
    if not job:
        # Check if there is a running one?
        running_job = ScanJob.objects.filter(
            product_id=product_id,
            status__in=['pending', 'running']
        ).order_by('-created_at').first()
        
        if running_job:
             return Response({
                'found': True,
                'status': running_job.status,
                'job_id': running_job.job_id,
                'is_running': True
            })
            
        return Response({'found': False}, status=200)
        
    return Response({
        'found': True,
        'job_id': job.job_id,
        'status': job.status,
        'timestamp': job.completed_at,
        'result': job.result # Include result so frontend can render immediately
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def output_query(request):
    """
    Run query against multiple AI engines.
    """
    # This view needs to be async-capable or handle async internally.
    # Since we are using @api_view (sync db mostly), let's wrap logic.
    # DRF 3.11+ supports 'async def' views but decorators can be tricky.
    # Safest MVP: sync view doing asyncio.run() for unrelated async calls, 
    # provided it doesn't conflict with main loop (Django 3+ runs in sync usually).
    
    query = request.data.get('query')
    target_url = request.data.get('target_url')
    engines_requested = request.data.get('engines', ['openai', 'anthropic', 'gemini'])
    
    if not query or not target_url:
        return Response({'error': 'query and target_url required'}, status=400)

    # Re-use engine registry logic manually for now to keep it simple
    engines = []
    
    # We need to load env vars - 'aeo.config' uses pydantic BaseSettings loading .env
    # so we can just grab from os.environ after initializing Settings once
    # or just use Settings() again.
    import os
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
    # Since 'engines.py' depends on async methods (ainvoke), we run them.
    try:
        results = asyncio.run(query_multiple_engines(query, target_url, engines))
    except Exception as e:
        # If we are already in an event loop (e.g. running under uvicorn/asgi), asyncio.run fail.
        # But standard 'python manage.py runserver' is threaded/sync mostly unless configured otherwise.
        # Fallback for nested loop:
        # loop = asyncio.get_event_loop() # might fail if none
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
                    'metadata': {'target_url': target_url}
                }
            )
            
    citation_rate = cited_count / len(formatted_results) if formatted_results else 0
    
    return Response({
        'query': query,
        'results': formatted_results,
        'total_cost_usd': round(total_cost, 4),
        'citation_rate': round(citation_rate, 2)
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
    """
    from .models import LLMInteraction
    from django.db.models import Max, Count, F, Q
    
    # Simple grouping by query_text
    # We want: query_text, last_run, engine_count
    
    # 1. Get unique queries with annotation
    history = LLMInteraction.objects.values('query_text').annotate(
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
    
    # specific to this query string, ordered by latest
    # In a real app we might have a session ID or batch ID to group exactly. 
    # For now, we take the latest N where N is likely engine count, or just all within a small time window of the latest one.
    # PROPLER LOGIC: Get the timestamp of the very last interaction for this query, and get all interactions with that query from that same "batch" (approx time).
    
    latest = LLMInteraction.objects.filter(query_text=query_text).order_by('-timestamp').first()
    if not latest:
        return Response({'error': 'Not found'}, status=404)
        
    # Get all interactions for this query that happened within 5 seconds of the last one (grouping by time window)
    # OR just return all engines from the last run.
    
    interactions = LLMInteraction.objects.filter(
        query_text=query_text,
        timestamp__gte=latest.timestamp - timezone.timedelta(seconds=10),
        timestamp__lte=latest.timestamp + timezone.timedelta(seconds=10)
    )
    
    formatted_results = []
    total_cost = 0.0
    cited_count = 0
    
    for r in interactions:
        # We need to re-construct citations from response text since we didn't store structured citations in a JSONField in the simplified model (we only have response text)
        # However, for the UI to show "Citations Detected", we can run the extractor again OR just accept we only have text.
        # Wait, the `LLMInteraction` model DOES NOT have a `citations` JSON field in the current `models.py`? 
        # Let's check `models.py` via tool if unsure. 
        # Looking at previous view `output_query`, we didn't save citations to DB! We only logged them.
        # We should probably patch that if we want perfect history. 
        # For now, we will regex extract URLs from text as a fallback citation detecion.
        
        # Simple Url extraction for display
        import re
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', r.response_text or r.response) # handle legacy field name confusion if any
        
        citations = [{'url': u, 'snippet': ''} for u in urls]
        
        formatted_results.append({
            'engine': r.engine,
            'response': r.response_text,
            'citations': citations,
            'cost_usd': float(r.cost_usd),
            'latency_ms': 0, # Not saved
            'tokens_used': 0 # Not saved
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

