from django.contrib import admin
from .models import LevelUpLog

@admin.register(LevelUpLog)
class LevelUpLogAdmin(admin.ModelAdmin):
    list_display = ['child', 'category', 'level', 'created_at']
    list_filter = ['category', 'level', 'created_at']
    search_fields = ['child__name']
    readonly_fields = ['created_at', 'updated_at']