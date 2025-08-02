from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(help_text='메시지 전송자 (llm 또는 child)')
    content = serializers.CharField(help_text='메시지 내용')
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'content', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True, help_text='채팅 메시지 목록')
    category = serializers.CharField(help_text='학습 카테고리')
    current_level = serializers.IntegerField(help_text='현재 레벨')
    scenario = serializers.CharField(help_text='상황극 내용')
    is_active = serializers.BooleanField(help_text='세션 활성 상태')
    progress_score = serializers.IntegerField(help_text='진행도 점수')
    
    class Meta:
        model = ChatSession
        fields = ['id', 'category', 'current_level', 'scenario', 'is_active', 'progress_score', 'messages']