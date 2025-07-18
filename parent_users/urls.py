from django.urls import path
from .views import LoginView, LogoutView, ParentUserView, ParentUserDetailView
urlpatterns = [
    path("login/", LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', ParentUserView.as_view(), name='signup, list-users'),
    path('me/', ParentUserDetailView.as_view(), name='parent-user-detail'),
]