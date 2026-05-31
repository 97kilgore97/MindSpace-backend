from django.contrib import admin
from .models import CrisisFlag, SMSLog


@admin.register(CrisisFlag)
class CrisisFlagAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'severity', 'source', 'status', 'created_at']
    list_filter   = ['severity', 'status', 'source']
    search_fields = ['user__display_name', 'trigger_text']
    ordering      = ['-created_at']
    readonly_fields = ['id', 'created_at', 'trigger_text', 'source_id']

    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
    mark_resolved.short_description = 'Mark selected flags as resolved'


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'type', 'status', 'sent_at']
    list_filter   = ['type', 'status']
    search_fields = ['recipient', 'message']
    ordering      = ['-sent_at']
    readonly_fields = ['id', 'sent_at', 'at_message_id']
