"""
accounts/views.py
All auth views: login, register (user + admin), profile.
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer, AdminRegisterSerializer,
    UserSerializer, CustomTokenSerializer,
)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/  →  { access, refresh, user }"""
    serializer_class = CustomTokenSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """POST /api/auth/register/ — create customer, saved to DB."""
    s = RegisterSerializer(data=request.data)
    if s.is_valid():
        user = s.save()
        return Response({'message': 'Account created.', 'user': UserSerializer(user).data},
                        status=status.HTTP_201_CREATED)
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_admin(request):
    """POST /api/auth/admin-register/ — create admin with secret key."""
    s = AdminRegisterSerializer(data=request.data)
    if s.is_valid():
        user = s.save()
        return Response({'message': 'Admin created.', 'user': UserSerializer(user).data},
                        status=status.HTTP_201_CREATED)
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """GET/PATCH /api/auth/profile/"""
    user = request.user
    if request.method == 'GET':
        return Response(UserSerializer(user).data)
    # Update
    for field in ('first_name', 'last_name', 'email'):
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()
    if 'phone' in request.data:
        try:
            user.profile.phone = request.data['phone']
            user.profile.save()
        except Exception:
            pass
    return Response(UserSerializer(user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """GET /api/auth/users/ — admin only."""
    if not request.user.is_staff:
        return Response({'error': 'Admin only'}, status=403)
    users = User.objects.select_related('profile').order_by('-date_joined')
    data  = []
    for u in users:
        row = UserSerializer(u).data
        row['date_joined'] = u.date_joined.strftime('%Y-%m-%d %H:%M')
        data.append(row)
    return Response({'count': len(data), 'results': data})
