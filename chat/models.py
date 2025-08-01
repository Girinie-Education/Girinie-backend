from django.db import models
from common.models import CommonModel
from child_users.models import ChildUser

class ChatSession(CommonModel):
    CATEGORIES = [
        ('order', '질서'),
        ('manners', '예절'),
        ('selfcare', '자조'),
        ('clean', '청결'),
        ('calm', '감정조절'),
        ('kindness', '존중'),
        ('saving', '절약'),
        ('eating', '식습관'),
    ]
    
    child = models.ForeignKey(ChildUser, on_delete=models.CASCADE, related_name='chat_sessions')
    category = models.CharField(max_length=20, choices=CATEGORIES)
    current_level = models.PositiveSmallIntegerField()
    scenario = models.TextField()
    is_active = models.BooleanField(default=True)
    progress_score = models.PositiveSmallIntegerField(default=0)
    
    def __str__(self):
        return f"{self.child.name} - {self.get_category_display()}"

class ChatMessage(CommonModel):
    SENDER_CHOICES = [
        ('llm', 'LLM'),
        ('child', 'Child'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    evaluation_score = models.PositiveSmallIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.session} - {self.sender}: {self.content[:50]}"