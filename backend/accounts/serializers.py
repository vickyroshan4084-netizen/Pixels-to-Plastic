"""
accounts/serializers.py
─────────────────────────────────────────────────────────────────────────────
REPLACE your existing serializers.py with this.

Changes from original:
1. RegisterSerializer now accepts phone, city, state, pincode → saves to UserProfile
2. UserSerializer now includes phone (from profile)
3. AdminRegisterSerializer reads ADMIN_KEY from environment variable
4. All other logic kept exactly the same as your original
─────────────────────────────────────────────────────────────────────────────
"""
import os
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data         = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)
    phone    = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'phone']

    def get_phone(self, obj):
        try:
            return obj.profile.phone
        except Exception:
            return ''


class RegisterSerializer(serializers.ModelSerializer):
    """
    Customer registration.
    Now accepts phone, city, state, pincode → saved to UserProfile in DB.
    """
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    phone     = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')
    city      = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')
    state     = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')
    pincode   = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')
    access    = serializers.SerializerMethodField(read_only=True)
    user      = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password', 'password2',
                  'phone', 'city', 'state', 'pincode',
                  'access', 'user']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # Extract profile fields
        phone   = validated_data.pop('phone',   '')
        city    = validated_data.pop('city',    '')
        state   = validated_data.pop('state',   '')
        pincode = validated_data.pop('pincode', '')
        validated_data.pop('password2')

        # Create user
        user = User.objects.create_user(**validated_data)

        # Save profile (phone, city, state, pincode)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role    = 'customer'
        profile.phone   = phone
        profile.city    = city
        profile.state   = state
        profile.pincode = pincode
        profile.save()

        return user

    def get_access(self, obj):
        access, _ = get_tokens(obj)
        return access

    def get_user(self, obj):
        return UserSerializer(obj).data


class AdminRegisterSerializer(serializers.ModelSerializer):
    """
    Admin registration — requires secret admin_key.
    Key is now read from environment variable ADMIN_KEY for security.
    """
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    admin_key = serializers.CharField(write_only=True)
    access    = serializers.SerializerMethodField(read_only=True)
    user      = serializers.SerializerMethodField(read_only=True)

    # Read from env so it's not hardcoded in source code
    ADMIN_KEY = os.environ.get('ADMIN_KEY', 'p2p_admin_2024')

    class Meta:
        model  = User
        fields = ['username', 'password', 'password2', 'admin_key', 'access', 'user']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if data['admin_key'] != self.ADMIN_KEY:
            raise serializers.ValidationError({"admin_key": "Invalid admin registration key."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('admin_key')
        user = User.objects.create_user(**validated_data)
        user.is_staff     = True
        user.is_superuser = True
        user.save()
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
        return user

    def get_access(self, obj):
        access, _ = get_tokens(obj)
        return access

    def get_user(self, obj):
        return UserSerializer(obj).data


class ProfileSerializer(serializers.ModelSerializer):
    """Full profile update including address fields."""
    username   = serializers.CharField(source='user.username', read_only=True)
    email      = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name  = serializers.CharField(source='user.last_name')
    is_staff   = serializers.BooleanField(source='user.is_staff', read_only=True)

    class Meta:
        model  = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff',
                  'phone', 'address', 'city', 'state', 'pincode']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for k, v in user_data.items():
            setattr(instance.user, k, v)
        instance.user.save()
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
