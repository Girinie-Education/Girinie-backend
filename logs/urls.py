from django.urls import path
from .views import LevelUpLogView, ChildLevelUpLogView

urlpatterns = [
    path('levelup/', LevelUpLogView.as_view(), name='levelup-logs'),
    path('levelup/child/<int:child_id>/', ChildLevelUpLogView.as_view(), name='child-levelup-logs'),
]