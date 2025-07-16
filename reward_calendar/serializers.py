from rest_framework import serializers
from .models import RewardCalendar

class RewardCalendarSerializer(serializers.ModelSerializer):
    sticker_label = serializers.SerializerMethodField()

    class Meta:
        model = RewardCalendar
        fields = [
            'id', 'child', 'date', 'sticker_type', 'sticker_label',
            'message', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'child', 'sticker_label', 'created_at', 'updated_at']

    def get_sticker_label(self, obj):
        return obj.get_sticker_type_display()