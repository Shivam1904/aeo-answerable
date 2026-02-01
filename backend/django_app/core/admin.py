from django.contrib import admin
from .models import ScanJob, LLMInteraction

@admin.register(ScanJob)
class ScanJobAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'created_at', 'pages_scanned')
    list_filter = ('status', 'mode')
    search_fields = ('url', 'job_id')

@admin.register(LLMInteraction)
class LLMInteractionAdmin(admin.ModelAdmin):
    list_display = ('engine', 'target_url', 'query_text', 'timestamp', 'cost_usd', 'success')
    list_filter = ('engine', 'success')
    search_fields = ('query_text', 'target_url', 'response_text')
    readonly_fields = ('timestamp',)
