"""
accounts/urls.py
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, register_user, register_admin, user_profile, list_users

urlpatterns = [
    path('login/',          LoginView.as_view(),   name='login'),
    path('register/',       register_user,         name='register'),
    path('admin-register/', register_admin,        name='admin-register'),
    path('profile/',        user_profile,          name='profile'),
    path('users/',          list_users,            name='users'),
    path('refresh/',        TokenRefreshView.as_view(), name='token-refresh'),
]
