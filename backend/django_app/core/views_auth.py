from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import AppUser, Product
from aeo.config import Settings
from aeo.output_monitoring.engines import create_openai_engine, create_anthropic_engine
import asyncio

# --- AI Helper (Inline for now) ---
# --- AI Helper (Inline for now) ---
async def generate_bio(domain: str, name: str) -> str:
    """Generate a short business bio using standard OpenAI engine."""
    try:
        settings = Settings()
        if not settings.openai_api_key:
            return ""
        
        # Real implementation:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        prompt = f"Write a short, professional business bio (max 2 sentences) for a company named '{name}' with domain '{domain}'. Focus on what they likely do."
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Bio gen failed: {e}")
        return ""

async def generate_competitors(business_bio: str, target_region: str, target_audience_age: str, gender_preference: str) -> list:
    """Generate top 5 competitors based on bio and store in DB."""
    try:
        settings = Settings()
        if not settings.openai_api_key:
            return []
            
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        prompt = f"""
        Based on the following business bio, list the top 5 real-world companies that are most similar or are direct competitors.
        Focus on companies that are likely to be cited by LLMs.
        
        Business Bio: "{business_bio}"
        Target Region: {target_region}
        Target Audience: {target_audience_age}
        Gender Preference: {gender_preference}
        
        Return ONLY a JSON array of objects with keys: "name", "domain", "reason".
        Example: [{{"name": "CompA", "domain": "compa.com", "reason": "..."}}]
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Flexible parsing
        results = data.get('companies', data.get('competitors', data))
        if isinstance(results, dict):
            for k, v in results.items():
                if isinstance(v, list):
                    results = v
                    break
        
        return results if isinstance(results, list) else []
        
    except Exception as e:
        print(f"Competitor gen failed: {e}")
        return []


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    """
    Simple login: accepts username, creates if not exists.
    """
    username = request.data.get('username')
    if not username:
        return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    user, created = AppUser.objects.get_or_create(username=username)
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'created_new': created
    })

@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def product_list_create_view(request):
    """
    GET: List products for a user_id (query param).
    POST: Create a new product for a user_id.
    """
    if request.method == 'GET':
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)
            
        products = Product.objects.filter(user_id=user_id).values(
            'id', 'name', 'domain', 'default_mode', 'created_at',
            'business_bio', 'is_bio_ai_generated', 'target_region', 'target_audience_age', 'gender_preference'
        )
        return Response(list(products))
        
    elif request.method == 'POST':
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        domain = request.data.get('domain')
        default_mode = request.data.get('default_mode', 'fast')
        
        # New Fields
        business_bio = request.data.get('business_bio', "").strip()
        target_region = request.data.get('target_region', "Global") or "Global"
        target_audience_age = request.data.get('target_audience_age', "All") or "All"
        gender_preference = request.data.get('gender_preference', "All") or "All"
        
        if not all([user_id, name, domain]):
            return Response({'error': 'user_id, name, and domain are required'}, status=400)
            
        user = get_object_or_404(AppUser, pk=user_id)
        
        # AI Bio Generation
        is_bio_ai_generated = False
        if not business_bio:
            # Trigger async generation (Sync for MVP so we can return it immediately)
            # In production, use Celery. Here we just wait a bit or run sync.
            try:
                # We'll run it synchronously for the response context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                business_bio = loop.run_until_complete(generate_bio(domain, name))
                loop.close()
                if business_bio:
                    is_bio_ai_generated = True
            except Exception as e:
                print(f"Failed to generate bio: {e}")
                
        # Generate Competitors (Async logic running sync for MVP response)
        competitors = []
        if business_bio:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                competitors = loop.run_until_complete(
                    generate_competitors(business_bio, target_region, target_audience_age, gender_preference)
                )
                loop.close()
            except Exception as e:
                print(f"Failed to auto-gen competitors: {e}")
        
        product = Product.objects.create(
            user=user, 
            name=name, 
            domain=domain, 
            default_mode=default_mode,
            business_bio=business_bio,
            is_bio_ai_generated=is_bio_ai_generated,
            target_region=target_region,
            target_audience_age=target_audience_age,
            gender_preference=gender_preference,
            competitors=competitors
        )
        
        return Response({
            'id': product.id,
            'name': product.name,
            'domain': product.domain,
            'default_mode': product.default_mode,
            'created_at': product.created_at,
            'business_bio': product.business_bio,
            'is_bio_ai_generated': product.is_bio_ai_generated,
            'target_region': product.target_region,
            'target_audience_age': product.target_audience_age,
            'gender_preference': product.gender_preference
        }, status=201)

@api_view(['GET', 'PUT'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_product_view(request, product_id):
    """
    GET: Get single product details.
    PUT: Update product details.
    """
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'GET':
        return Response({
            'id': product.id,
            'name': product.name,
            'domain': product.domain,
            'default_mode': product.default_mode,
            'user_id': product.user_id, 
            'created_at': product.created_at,
            'business_bio': product.business_bio,
            'is_bio_ai_generated': product.is_bio_ai_generated,
            'target_region': product.target_region,
            'target_audience_age': product.target_audience_age,
            'gender_preference': product.gender_preference
        })
        
    elif request.method == 'PUT':
        # Update fields
        product.name = request.data.get('name', product.name)
        product.domain = request.data.get('domain', product.domain)
        product.default_mode = request.data.get('default_mode', product.default_mode)
        product.business_bio = request.data.get('business_bio', product.business_bio)
        product.target_region = request.data.get('target_region', product.target_region)
        product.target_audience_age = request.data.get('target_audience_age', product.target_audience_age)
        product.gender_preference = request.data.get('gender_preference', product.gender_preference)
        
        # If user manually edited bio, unmark AI flag
        if 'business_bio' in request.data:
            product.is_bio_ai_generated = False
        
        # Regenerate competitors if critical fields changed
        # We check if bio, region, or audience changed significantly
        # For simplicity, if PUT request comes in with these fields, we trigger re-gen
        should_regen_competitors = any(k in request.data for k in ['business_bio', 'target_region', 'target_audience_age'])
        
        if should_regen_competitors and product.business_bio:
             try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                new_competitors = loop.run_until_complete(
                    generate_competitors(
                        product.business_bio, 
                        product.target_region, 
                        product.target_audience_age, 
                        product.gender_preference
                    )
                )
                loop.close()
                if new_competitors:
                    product.competitors = new_competitors
             except Exception as e:
                print(f"Failed to re-gen competitors: {e}")
            
        product.save()
        
        return Response({
            'id': product.id,
            'message': 'Product updated'
        })
