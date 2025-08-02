from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from child_users.models import ChildUser
from logs.models import LevelUpLog
import pytz

class Command(BaseCommand):
    help = '전날 레벨업하지 않은 아이들의 streak을 0으로 리셋'

    def handle(self, *args, **options):
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # 어제 레벨업한 아이들의 ID 목록
        children_with_levelup = LevelUpLog.objects.filter(
            created_at__date=yesterday
        ).values_list('child_id', flat=True).distinct()

        utc_now = timezone.now()
        print(utc_now)
        kst = pytz.timezone('Asia/Seoul')
        kst_now = utc_now.astimezone(kst)
        print(kst_now)
        print(children_with_levelup)
        
        # 어제 레벨업하지 않은 아이들의 streak을 0으로 리셋
        reset_count = ChildUser.objects.exclude(
            id__in=children_with_levelup
        ).update(streak=0)
        
        self.stdout.write(
            self.style.SUCCESS(f'{reset_count}명의 아이들의 streak이 리셋되었습니다.')
        )