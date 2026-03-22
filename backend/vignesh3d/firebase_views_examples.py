"""
Firebase Integration Examples — Pixels to Plastic (P2P)
Server-side usage patterns for common Firebase operations
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from vignesh3d.firebase_config import get_auth, get_firestore, get_storage
import json

# ═════════════════════════════════════════════════════════════════════════════
# 1️⃣ VERIFY FIREBASE TOKEN FROM FRONTEND
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
def verify_firebase_token(request):
    """
    Verify a Firebase token sent from the frontend
    Frontend sends: Authorization: Bearer <firebase_id_token>
    """
    try:
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header.replace('Bearer ', '')
        
        if not token:
            return Response({'error': 'No token provided'}, status=400)
        
        # Verify with Firebase
        decoded_token = get_auth().verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        return Response({
            'success': True,
            'uid': uid,
            'email': email,
            'message': 'Token verified successfully'
        })
    except Exception as e:
        return Response({
            'error': f'Invalid token: {str(e)}'
        }, status=401)


# ═════════════════════════════════════════════════════════════════════════════
# 2️⃣ GET USER PROFILE FROM FIRESTORE
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get user profile data from Firestore
    Collection: users
    Document: user_id (Firebase UID)
    """
    try:
        # Extract Firebase UID from JWT token in request
        # You may need to get this from the authenticated user
        user_id = request.user.id  # Or extract from Firebase token
        
        db = get_firestore()
        doc = db.collection('users').document(str(user_id)).get()
        
        if doc.exists:
            user_data = doc.to_dict()
            return Response({
                'success': True,
                'data': user_data
            })
        else:
            return Response({
                'error': 'User profile not found'
            }, status=404)
    except Exception as e:
        return Response({
            'error': f'Error fetching profile: {str(e)}'
        }, status=500)


# ═════════════════════════════════════════════════════════════════════════════
# 3️⃣ SAVE/UPDATE USER PROFILE IN FIRESTORE
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update user profile in Firestore
    Expected request body:
    {
        "name": "John Doe",
        "phone": "+919876543210",
        "address": "123 Main St",
        "city": "Bangalore",
        "bio": "3D artist and designer"
    }
    """
    try:
        user_id = str(request.user.id)
        user_data = request.data
        
        db = get_firestore()
        db.collection('users').document(user_id).set(user_data, merge=True)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user_id': user_id
        })
    except Exception as e:
        return Response({
            'error': f'Error updating profile: {str(e)}'
        }, status=500)


# ═════════════════════════════════════════════════════════════════════════════
# 4️⃣ UPLOAD PROFILE PHOTO TO STORAGE
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_photo(request):
    """
    Upload user profile photo to Firebase Storage
    Send file in request: files['photo']
    """
    try:
        if 'photo' not in request.FILES:
            return Response({
                'error': 'No photo file provided'
            }, status=400)
        
        photo_file = request.FILES['photo']
        user_id = str(request.user.id)
        
        # Upload to Storage
        bucket = get_storage()
        blob = bucket.blob(f'profile_photos/{user_id}/{photo_file.name}')
        blob.upload_from_string(
            photo_file.read(),
            content_type=photo_file.content_type
        )
        
        # Make file public
        blob.make_public()
        
        # Save URL to Firestore
        db = get_firestore()
        db.collection('users').document(user_id).update({
            'profile_photo_url': blob.public_url
        })
        
        return Response({
            'success': True,
            'message': 'Photo uploaded successfully',
            'url': blob.public_url
        })
    except Exception as e:
        return Response({
            'error': f'Error uploading photo: {str(e)}'
        }, status=500)


# ═════════════════════════════════════════════════════════════════════════════
# 5️⃣ SAVE ORDER TO FIRESTORE
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_order_to_firestore(request):
    """
    Save order data to Firestore
    Expected: order_id, user_id, items, total, status
    """
    try:
        order_data = {
            'user_id': str(request.user.id),
            'items': request.data.get('items', []),
            'total': request.data.get('total', 0),
            'status': 'pending',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'shipping_address': request.data.get('shipping_address', {})
        }
        
        db = get_firestore()
        order_ref = db.collection('orders').document()
        order_ref.set(order_data)
        
        return Response({
            'success': True,
            'order_id': order_ref.id,
            'message': 'Order saved successfully'
        })
    except Exception as e:
        return Response({
            'error': f'Error saving order: {str(e)}'
        }, status=500)


# ═════════════════════════════════════════════════════════════════════════════
# 6️⃣ QUERY FIRESTORE (e.g., Get all orders by user)
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    """
    Get all orders for the current user from Firestore
    """
    try:
        user_id = str(request.user.id)
        db = get_firestore()
        
        # Query orders collection where user_id matches
        orders = db.collection('orders').where('user_id', '==', user_id).stream()
        
        orders_list = []
        for order in orders:
            order_data = order.to_dict()
            order_data['id'] = order.id
            orders_list.append(order_data)
        
        return Response({
            'success': True,
            'count': len(orders_list),
            'orders': orders_list
        })
    except Exception as e:
        return Response({
            'error': f'Error fetching orders: {str(e)}'
        }, status=500)


# ═════════════════════════════════════════════════════════════════════════════
# 7️⃣ DELETE USER DATA FROM FIRESTORE
# ═════════════════════════════════════════════════════════════════════════════

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_profile(request):
    """
    Delete user profile from Firestore (GDPR compliance)
    """
    try:
        user_id = str(request.user.id)
        db = get_firestore()
        
        db.collection('users').document(user_id).delete()
        
        return Response({
            'success': True,
            'message': 'User profile deleted successfully'
        })
    except Exception as e:
        return Response({
            'error': f'Error deleting profile: {str(e)}'
        }, status=500)


# ═════════════════════════════════════════════════════════════════════════════
# SETUP: Add these to your urls.py
# ═════════════════════════════════════════════════════════════════════════════

"""
from django.urls import path
from . import firebase_views

urlpatterns = [
    path('firebase/verify-token/', firebase_views.verify_firebase_token),
    path('firebase/profile/', firebase_views.get_user_profile),
    path('firebase/profile/update/', firebase_views.update_user_profile),
    path('firebase/profile/photo/', firebase_views.upload_profile_photo),
    path('firebase/orders/', firebase_views.get_user_orders),
    path('firebase/orders/save/', firebase_views.save_order_to_firestore),
    path('firebase/profile/delete/', firebase_views.delete_user_profile),
]
"""
