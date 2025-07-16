from django.urls import path
from .views import RewardCalendarMonthView, RewardCalendarDayView

urlpatterns = [
    path('<int:child_id>/<int:year>/<int:month>/', RewardCalendarMonthView.as_view(), name='reward-calendar-month'),
    path('<int:child_id>/', RewardCalendarDayView.as_view(), name='reward-calendar-day'),
]