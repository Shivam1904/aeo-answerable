from django.contrib import admin
from django.urls import path
from core import views
from core import views_auth

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & Products
    path('api/auth/login', views_auth.login_view),
    path('api/products', views_auth.product_list_create_view),
    path('api/products/<int:product_id>', views_auth.get_product_view),
    
    # Scans
    path('api/scan', views.start_scan),
    path('api/scan/<str:job_id>', views.get_scan_status),
    path('api/products/<int:product_id>/latest-scan', views.get_latest_scan_for_product),

    # Output Monitoring API (subset for verifying)
    path('api/output-monitoring/query', views.output_query),
    path('api/output-monitoring/available-engines/', views.available_engines),
    path('api/output-monitoring/budget', views.get_budget),
    path('api/output-monitoring/history', views.get_query_history),
    path('api/output-monitoring/history/details', views.get_history_details),
    
    # Health
    path('api/health', lambda r: __import__('django.http').HttpResponse('ok')),
]
