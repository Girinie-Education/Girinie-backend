
from django.contrib import admin
from .models import RewardCalendar

@admin.register(RewardCalendar)
class RewardCalendarAdmin(admin.ModelAdmin):
    list_display = ('child', 'date', 'sticker_type', 'message')
    list_filter = ('child', 'date', 'sticker_type')
    search_fields = ('child__name', 'message')
    ordering = ('-date',)