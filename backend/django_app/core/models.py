from django.db import models
from django.utils import timezone
import uuid

class AppUser(models.Model):
    """
    Simple user model for the MVP.
    """
    username = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Product(models.Model):
    """
    A product/website belonging to a user.
    """
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    domain = models.URLField(max_length=500, help_text="The main domain of the product (e.g., https://example.com)")
    default_mode = models.CharField(max_length=20, default='fast', choices=[('fast', 'Fast'), ('rendered', 'Rendered')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ScanJob(models.Model):
    """
    Stores the status and result of a crawling scan.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('complete', 'Complete'),
        ('error', 'Error'),
    ]

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Link to Product. Optional for now to avoid immediate breakage if manual scans used, 
    # but strictly required for the new flow.
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='scans')
    
    url = models.URLField(max_length=500)
    mode = models.CharField(max_length=20, default='fast')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Store the large JSON result blob
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    
    # Simple progress tracking
    pages_scanned = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.url} ({self.status})"


# OutputQuery removed as per user request for single-table architecture



class LLMInteraction(models.Model):
    """
    Detailed log of a single LLM interaction/request.
    Used for analytics, cost tracking, and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Link to Product for better cost allocation
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    # User Request Context (Merged from OutputQuery)
    target_url = models.URLField(max_length=500, default="https://example.com")
    query_text = models.TextField(default="")
    
    # Engine details
    engine = models.CharField(max_length=50, help_text="e.g. openai, anthropic, gemini")
    model_name = models.CharField(max_length=100, blank=True, null=True, help_text="Specific model used e.g. gpt-4o")
    
    # Request/Response
    prompt_text = models.TextField(help_text="The actual prompt sent to the LLM")
    response_text = models.TextField(help_text="The raw response received")
    
    # Usage Stats
    tokens_input = models.IntegerField(default=0)
    tokens_output = models.IntegerField(default=0)
    cost_usd = models.FloatField(default=0.0)
    latency_ms = models.IntegerField(default=0)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Context
    metadata = models.JSONField(default=dict, blank=True, help_text="Extra context like job_id, user_id, etc.")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['engine', 'timestamp']),
            models.Index(fields=['success']),
        ]

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.engine} at {self.timestamp.strftime('%H:%M:%S')}"
