from django.contrib import admin
from .models import SupportGroup, ChatMessage

@admin.register(SupportGroup)
class SupportGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'group', 'recipient', 'is_anonymous', 'created_at']
    list_filter = ['is_anonymous']
