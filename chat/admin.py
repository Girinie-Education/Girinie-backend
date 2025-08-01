from django.contrib import admin
from .models import ChatSession, ChatMessage

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['child', 'category', 'current_level', 'is_active', 'progress_score', 'created_at']
    list_filter = ['category', 'is_active', 'current_level']
    search_fields = ['child__name']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender', 'content_preview', 'evaluation_score', 'created_at']
    list_filter = ['sender', 'evaluation_score']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'