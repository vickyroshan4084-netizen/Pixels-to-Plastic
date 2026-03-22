"""
accounts/views.py
─────────────────────────────────────────────────────────────────────────────
REPLACE your existing views.py with this.
Added: LoginView, UsersListView (admin only user list).
All original views kept exactly the same.
─────────────────────────────────────────────────────────────────────────────
"""
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserProfile
from .serializers import (
    RegisterSerializer, AdminRegisterSerializer,
    ProfileSerializer, UserSerializer, MyTokenObtainPairSerializer,
)
import firebase_admin
from firebase_admin import auth as firebase_auth
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ → { access, refresh, user }"""
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/"""
    queryset           = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class   = RegisterSerializer


class AdminRegisterView(generics.CreateAPIView):
    """POST /api/auth/admin-register/"""
    queryset           = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class   = AdminRegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /api/auth/profile/"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ProfileSerializer

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UsersListView(APIView):
    """GET /api/auth/users/ — admin only, lists all registered customers"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required.'}, status=403)

        users = User.objects.select_related('profile').order_by('-date_joined')
        data  = []
        for u in users:
            row = UserSerializer(u).data
            row['date_joined'] = u.date_joined.strftime('%d %b %Y  %H:%M')
            try:
                row['city']    = u.profile.city
                row['state']   = u.profile.state
                row['pincode'] = u.profile.pincode
                row['address'] = u.profile.address
            except Exception:
                pass
            data.append(row)

        return Response({'count': len(data), 'results': data})


class FirebaseAdminLoginView(APIView):
    """POST /api/auth/firebase-admin/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get('idToken')
        if not id_token:
            return Response({'error': 'No Firebase token provided'}, status=400)

        try:
            # Verify the Firebase token
            decoded_token = firebase_auth.verify_id_token(id_token)
            email = decoded_token.get('email')

            if not email:
                return Response({'error': 'No email found in token'}, status=400)

            # Get or create user
            user, created = User.objects.get_or_create(username=email, defaults={'email': email})

            # Force superuser access for authenticating via Firebase
            user.is_superuser = True
            user.is_staff = True
            user.save()

            # Ensure profile exists
            UserProfile.objects.get_or_create(user=user)

            # Generate Django JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Use UserSerializer for payload
            user_data = UserSerializer(user).data

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=401)
