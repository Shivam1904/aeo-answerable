from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import AppUser, Product

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
            
        products = Product.objects.filter(user_id=user_id).values('id', 'name', 'domain', 'default_mode', 'created_at')
        return Response(list(products))
        
    elif request.method == 'POST':
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        domain = request.data.get('domain')
        default_mode = request.data.get('default_mode', 'fast')
        
        if not all([user_id, name, domain]):
            return Response({'error': 'user_id, name, and domain are required'}, status=400)
            
        user = get_object_or_404(AppUser, pk=user_id)
        
        # Check if domain exists for this user? Maybe not strict validation yet.
        product = Product.objects.create(user=user, name=name, domain=domain, default_mode=default_mode)
        
        return Response({
            'id': product.id,
            'name': product.name,
            'domain': product.domain,
            'default_mode': product.default_mode,
            'created_at': product.created_at
        }, status=201)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_product_view(request, product_id):
    """
    Get single product details.
    """
    product = get_object_or_404(Product, pk=product_id)
    return Response({
        'id': product.id,
        'name': product.name,
        'domain': product.domain,
        'default_mode': product.default_mode,
        'user_id': product.user_id, 
        'created_at': product.created_at
    })
