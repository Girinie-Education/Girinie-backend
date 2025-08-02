from rest_framework import serializers
from .models import LevelUpLog

class LevelUpLogSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.name', read_only=True, help_text='아이 이름')
    category_display = serializers.CharField(source='get_category_display', read_only=True, help_text='카테고리 한글명')
    
    class Meta:
        model = LevelUpLog
        fields = ['id', 'child_name', 'category', 'category_display', 'level', 'created_at']