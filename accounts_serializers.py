"""
accounts/serializers.py
User registration now properly saves all data to the database.
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Change this key to protect admin registration
ADMIN_KEY = 'p2p_admin_2024'


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'phone']

    def get_phone(self, obj):
        try:
            return obj.profile.phone
        except Exception:
            return ''


class RegisterSerializer(serializers.ModelSerializer):
    """Customer registration — saves user + phone to database."""
    password = serializers.CharField(write_only=True, min_length=6)
    phone    = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        user  = User.objects.create_user(
            username   = validated_data['username'],
            email      = validated_data.get('email', ''),
            password   = validated_data['password'],
            first_name = validated_data.get('first_name', ''),
            last_name  = validated_data.get('last_name', ''),
            is_staff   = False,
        )
        # Save phone to profile
        try:
            from accounts.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if phone:
                profile.phone = phone
                profile.save()
        except Exception:
            pass
        return user


class AdminRegisterSerializer(serializers.ModelSerializer):
    """Admin registration — requires secret admin_key."""
    password  = serializers.CharField(write_only=True, min_length=6)
    admin_key = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'admin_key']

    def validate_admin_key(self, value):
        if value != ADMIN_KEY:
            raise serializers.ValidationError("Invalid admin key.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('admin_key')
        return User.objects.create_superuser(
            username = validated_data['username'],
            email    = validated_data.get('email', ''),
            password = validated_data['password'],
        )


class CustomTokenSerializer(TokenObtainPairSerializer):
    """Login — returns tokens + user info."""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
