from django.contrib import admin
from django.urls import path
from core import views_auth
from core import views_scan
from core import views_monitoring

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & Products
    path('api/auth/login', views_auth.login_view),
    path('api/products', views_auth.product_list_create_view),
    path('api/products/<int:product_id>', views_auth.get_product_view),
    
    # Scans
    path('api/scan', views_scan.start_scan),
    path('api/scan/<str:job_id>', views_scan.get_scan_status),
    path('api/products/<int:product_id>/latest-scan', views_scan.get_latest_scan_for_product),

    # Output Monitoring API (subset for verifying)
    path('api/output-monitoring/analyze', views_monitoring.analyze_brand_view),
    path('api/output-monitoring/query', views_monitoring.output_query),
    path('api/output-monitoring/available-engines/', views_monitoring.available_engines),
    path('api/output-monitoring/budget', views_monitoring.get_budget),
    path('api/output-monitoring/history', views_monitoring.get_query_history),
    path('api/output-monitoring/history/details', views_monitoring.get_history_details),
    path('api/output-monitoring/history/delete', views_monitoring.delete_history),
    path('api/output-monitoring/competitors', views_monitoring.get_similar_companies),
    path('api/output-monitoring/competitive-query', views_monitoring.competitive_query),
    
    # Health
    path('api/health', lambda r: __import__('django.http').HttpResponse('ok')),
]
