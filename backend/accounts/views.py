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

    # Whitelist of emails that are allowed admin access via Firebase
    ADMIN_EMAILS = [
        'vickyroshan4084@gmail.com',
    ]

    def post(self, request):
        id_token = request.data.get('idToken')
        email_direct = request.data.get('email')

        if not id_token and not email_direct:
            return Response({'error': 'No Firebase token or email provided'}, status=400)

        email = None

        # Path 1: Try Firebase token verification (requires service account)
        if id_token:
            try:
                if firebase_admin._apps:
                    decoded_token = firebase_auth.verify_id_token(id_token)
                    email = decoded_token.get('email')
                else:
                    # Firebase Admin not initialized — fall through to email path
                    pass
            except Exception as e:
                # Verification failed
                return Response({'error': f'Firebase token error: {str(e)}'}, status=401)

        # Path 2: Direct email (from frontend Firebase who already authenticated)
        if not email and email_direct:
            email = email_direct

        if not email:
            return Response({'error': 'Could not determine email from request'}, status=400)

        # Security: Only allow whitelisted admin emails
        if email.lower() not in [e.lower() for e in self.ADMIN_EMAILS]:
            return Response({'error': 'This email is not authorized for admin access.'}, status=403)

        # Get or create Django user
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})

        # Force superuser access
        user.is_superuser = True
        user.is_staff = True
        if not user.has_usable_password():
            user.set_unusable_password()
        user.save()

        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user)

        # Generate Django JWT tokens
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        })
