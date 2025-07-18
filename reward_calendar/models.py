from django.db import models
from common.models import CommonModel
from child_users.models import ChildUser

# Create your models here.

class RewardCalendar(CommonModel):
    STICKER_CHOICES = [
        (1, '조금 더 노력해봐요'),
        (2, '잘하고 있어요'),
        (3, '참 잘했어요'),
        (4, '아주 훌륭해요'),
        (5, '정말 최고예요'),
    ]

    child = models.ForeignKey(
        ChildUser,
        on_delete=models.CASCADE,
        related_name='reward_calendars'
    )
    date = models.DateField()
    sticker_type = models.PositiveSmallIntegerField(choices=STICKER_CHOICES)
    message = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.child.name} - {self.date} - {self.get_sticker_type_display()}"