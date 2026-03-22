"""
accounts/urls.py
─────────────────────────────────────────────────────────────────────────────
REPLACE your existing urls.py with this.
Added: login, refresh, verify, users endpoints.
─────────────────────────────────────────────────────────────────────────────
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import RegisterView, AdminRegisterView, ProfileView, LoginView, UsersListView, FirebaseAdminLoginView

urlpatterns = [
    path('login/',          LoginView.as_view(),        name='login'),
    path('firebase-admin/', FirebaseAdminLoginView.as_view(), name='firebase-admin'),
    path('register/',       RegisterView.as_view(),     name='register'),
    path('admin-register/', AdminRegisterView.as_view(),name='admin-register'),
    path('profile/',        ProfileView.as_view(),      name='profile'),
    path('users/',          UsersListView.as_view(),    name='users'),
    path('refresh/',        TokenRefreshView.as_view(), name='token-refresh'),
    path('verify/',         TokenVerifyView.as_view(),  name='token-verify'),
]
