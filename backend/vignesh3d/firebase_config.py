"""
Firebase Admin SDK Configuration — Pixels to Plastic (P2P)
Server-side operations for user authentication, Firestore, Storage, etc.
"""

import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from django.conf import settings
import json
import os

# ─── Firebase Configuration (same as frontend) ────────────────────────────
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDvtXnRyLVdG98uXUVsuYmWBpeFUfGEzJ0",
    "authDomain": "pixal-to-plastic.firebaseapp.com",
    "projectId": "pixal-to-plastic",
    "storageBucket": "pixal-to-plastic.firebasestorage.app",
    "messagingSenderId": "269644781419",
    "appId": "1:269644781419:web:7409155bd0ac5009d0de2e"
}

# ─── Firebase Service Account Key ─────────────────────────────────────────
# IMPORTANT: Download your service account key from Firebase Console:
# 1. Go to Firebase Console > Project Settings > Service Accounts
# 2. Click "Generate New Private Key" and save as 'firebase-service-account.json'
# 3. Place the file in backend/vignesh3d/ directory
# 4. Add 'firebase-service-account.json' to your .gitignore

SERVICE_ACCOUNT_KEY_PATH = os.path.join(
    os.path.dirname(__file__),
    'firebase-service-account.json'
)

# ─── Initialize Firebase Admin SDK ─────────────────────────────────────────
def initialize_firebase():
    """Initialize Firebase Admin SDK if not already done"""
    if not firebase_admin._apps:
        try:
            if os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
                # Use service account key (recommended for production)
                cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': FIREBASE_CONFIG['storageBucket']
                })
                print("✓ Firebase Admin SDK initialized with service account key")
            else:
                print("⚠ Warning: firebase-service-account.json not found")
                print("  Server-side Firebase operations will be limited")
                print("  To enable all features, download your service account key from Firebase Console")
        except Exception as e:
            print(f"✗ Error initializing Firebase: {str(e)}")

# Initialize on import
initialize_firebase()

# ─── Firebase Services (use these in your views) ───────────────────────────
def get_auth():
    """Get Firebase Auth instance for user management"""
    try:
        return auth
    except Exception as e:
        print(f"Error getting Firebase Auth: {e}")
        return None

def get_firestore():
    """Get Firestore instance for database operations"""
    try:
        if firebase_admin._apps:
            return firestore.client()
        else:
            print("Firebase not initialized")
            return None
    except Exception as e:
        print(f"Error getting Firestore: {e}")
        return None

def get_storage():
    """Get Firebase Storage bucket instance"""
    try:
        if firebase_admin._apps:
            return storage.bucket()
        else:
            print("Firebase not initialized")
            return None
    except Exception as e:
        print(f"Error getting Storage: {e}")
        return None

# ─── Example Usage in Django Views ────────────────────────────────────────
"""
# In your views.py:

from vignesh3d.firebase_config import get_auth, get_firestore, get_storage

# Verify Firebase token from frontend
def verify_user_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    try:
        decoded_token = get_auth().verify_id_token(token)
        user_id = decoded_token['uid']
        # Process user...
    except:
        return Response({'error': 'Invalid token'}, status=401)

# Get user data from Firestore
def get_user_profile(user_id):
    db = get_firestore()
    doc = db.collection('users').document(user_id).get()
    return doc.to_dict() if doc.exists else None

# Upload file to Firebase Storage
def upload_profile_photo(user_id, file):
    bucket = get_storage()
    blob = bucket.blob(f'user_photos/{user_id}.jpg')
    blob.upload_from_string(file.read(), content_type='image/jpeg')
    return blob.public_url
"""
