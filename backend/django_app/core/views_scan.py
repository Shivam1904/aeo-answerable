from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import ScanJob
from django.shortcuts import get_object_or_404
import asyncio
import threading

# Bridge to existing logic
# Add parent dir to path to import 'aeo' package
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from aeo.config import Settings
from aeo.crawler import Crawler
from aeo.rendered_crawler import RenderedCrawler
from aeo.readiness import calculate_ai_readiness

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
        
        # Calculate Readiness Score (Integrated Task 2)
        readiness_data = calculate_ai_readiness(result)
        
        ScanJob.objects.filter(job_id=job_id).update(
            status='complete',
            result=result,
            ai_readiness_score=readiness_data['score'],
            readiness_summary=readiness_data['breakdown'],
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
        'ai_readiness_score': job.ai_readiness_score,
        'readiness_summary': job.readiness_summary,
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
        'ai_readiness_score': job.ai_readiness_score,
        'readiness_summary': job.readiness_summary,
        'result': job.result # Include result so frontend can render immediately
    })
