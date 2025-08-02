from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.ChatSessionView.as_view(), name='start_chat'),
    path('message/', views.ChatMessageView.as_view(), name='send_message'),
    path('history/<int:child_id>/', views.ChatHistoryView.as_view(), name='chat_history'),
]