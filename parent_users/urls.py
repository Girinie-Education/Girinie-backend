from django.urls import path
from .views import LoginView, LogoutView, ParentUserView, ParentUserDetailView, FindUsernameView, ResetPasswordView, ResetPasswordConfirmView
urlpatterns = [
    path("login/", LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', ParentUserView.as_view(), name='signup, list-users'),
    path('me/', ParentUserDetailView.as_view(), name='parent-user-detail'),
    path('find-username/', FindUsernameView.as_view(), name='find-username'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-confirm/<str:uid>/<str:token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
]