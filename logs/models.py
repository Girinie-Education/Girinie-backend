from django.db import models
from common.models import CommonModel
from child_users.models import ChildUser

class LevelUpLog(CommonModel):
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
    
    child = models.ForeignKey(ChildUser, on_delete=models.CASCADE, related_name='levelup_logs')
    category = models.CharField(max_length=20, choices=CATEGORIES)
    level = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.child.name} - {self.get_category_display()} 레벨 {self.level}"