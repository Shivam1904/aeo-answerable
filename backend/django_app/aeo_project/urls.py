from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Scan API
    path('api/scan', views.start_scan),
    path('api/scan/<str:job_id>', views.get_scan_status),
    
    # Output Monitoring API (subset for verifying)
    path('api/output-monitoring/query', views.output_query),
    path('api/output-monitoring/available-engines/', views.available_engines),
    path('api/output-monitoring/budget', views.get_budget),
    path('api/output-monitoring/history', views.get_query_history),
    path('api/output-monitoring/history/details', views.get_history_details),
    
    # Health
    path('api/health', lambda r: __import__('django.http').HttpResponse('ok')),
]
