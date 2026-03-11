# Firebase Integration Guide — Pixels to Plastic (P2P)

## Overview

This project uses **Firebase** for both client-side and server-side operations:

- **Frontend (Web)**: Firebase SDK for authentication, Firestore, and Storage
- **Backend (Django)**: Firebase Admin SDK for server-side operations

## Frontend Setup (Already Done ✅)

Firebase is initialized in all HTML files:
- `frontend/admin-login.html`
- `frontend/index.html`
- `frontend/admin.html`

### Firebase Config (Frontend)
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDvtXnRyLVdG98uXUVsuYmWBpeFUfGEzJ0",
  authDomain: "pixal-to-plastic.firebaseapp.com",
  projectId: "pixal-to-plastic",
  storageBucket: "pixal-to-plastic.firebasestorage.app",
  messagingSenderId: "269644781419",
  appId: "1:269644781419:web:7409155bd0ac5009d0de2e"
};
```

---

## Backend Setup (Server-side)

### Step 1: Install Firebase Admin SDK
✅ **Already installed** in `requirements.txt`

```bash
pip install firebase-admin>=6.0.0
```

### Step 2: Get Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select **pixal-to-plastic** project
3. Settings ⚙️ → **Service Accounts** tab
4. Click **Generate New Private Key** (bottom of page)
5. A JSON file will download automatically

### Step 3: Place Service Account Key

Save the downloaded JSON file as:
```
backend/vignesh3d/firebase-service-account.json
```

### Step 4: Protect Your Key!

Add to `.gitignore` (already done):
```
firebase-service-account.json
backend/vignesh3d/firebase-service-account.json
```

**⚠️ IMPORTANT**: Never commit API keys to GitHub!

---

## Using Firebase in Django Views

### Setup

```python
from vignesh3d.firebase_config import get_auth, get_firestore, get_storage
```

### 1. Verify Firebase Token

```python
from rest_framework.decorators import api_view
from vignesh3d.firebase_config import get_auth

@api_view(['POST'])
def verify_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    try:
        decoded_token = get_auth().verify_id_token(token)
        uid = decoded_token['uid']
        return Response({'success': True, 'uid': uid})
    except:
        return Response({'error': 'Invalid token'}, status=401)
```

### 2. Work with Firestore (Database)

```python
from vignesh3d.firebase_config import get_firestore

# Get data
db = get_firestore()
doc = db.collection('users').document('user_id').get()
if doc.exists:
    user_data = doc.to_dict()

# Save data
db.collection('users').document('user_id').set({
    'name': 'John Doe',
    'email': 'john@example.com'
})

# Update data
db.collection('users').document('user_id').update({
    'phone': '9876543210'
})

# Query data
users = db.collection('users').where('city', '==', 'Bangalore').stream()
for user in users:
    print(user.to_dict())

# Delete data
db.collection('users').document('user_id').delete()
```

### 3. Upload Files to Storage

```python
from vignesh3d.firebase_config import get_storage

bucket = get_storage()

# Upload file
blob = bucket.blob('profile_photos/user_123.jpg')
blob.upload_from_string(file_data, content_type='image/jpeg')

# Make public
blob.make_public()

# Get URL
print(blob.public_url)

# Download file
blob.download_to_filename('local_file.jpg')
```

---

## Common Firestore Collections

Here's a suggested structure:

```
firestore/
├── users/
│   └── {uid}/
│       ├── name: "John Doe"
│       ├── email: "john@example.com"
│       ├── phone: "9876543210"
│       └── profile_photo_url: "https://..."
│
├── orders/
│   └── {order_id}/
│       ├── user_id: "uid"
│       ├── items: [{product_id, quantity, price}]
│       ├── total: 5000
│       ├── status: "pending" | "completed" | "cancelled"
│       ├── timestamp: 2026-03-09T10:30:00Z
│       └── shipping_address: {...}
│
├── products/
│   └── {product_id}/
│       ├── name: "3D Model"
│       ├── price: 1000
│       ├── category: "Miniatures"
│       └── photos: ["url1", "url2"]
│
└── reviews/
    └── {review_id}/
        ├── user_id: "uid"
        ├── product_id: "product_id"
        ├── rating: 5
        ├── text: "Amazing product!"
        └── timestamp: 2026-03-09T10:30:00Z
```

---

## Authentication Flow

### Frontend (JavaScript)
```javascript
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-auth.js";

const auth = getAuth();
signInWithEmailAndPassword(auth, email, password)
  .then(userCredential => {
    const idToken = userCredential.user.getIdToken();
    // Send idToken to backend
    fetch('/api/verify-token/', {
      headers: { 'Authorization': `Bearer ${idToken}` }
    });
  });
```

### Backend (Django)
```python
# Verify the token
decoded_token = get_auth().verify_id_token(idToken)
uid = decoded_token['uid']
email = decoded_token['email']
```

---

## Firestore Security Rules

In Firebase Console → Firestore → Rules:

```typescript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{uid} {
      allow read, write: if request.auth.uid == uid;
    }

    // Anyone can read products
    match /products/{document=**} {
      allow read: if true;
    }

    // Orders can only be accessed by owner
    match /orders/{orderId} {
      allow read, write: if request.auth.uid == resource.data.user_id;
    }
  }
}
```

---

## Real-time Listeners (Frontend)

```javascript
import { getFirestore, collection, onSnapshot } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-firestore.js";

const db = getFirestore();
const userRef = doc(db, "users", uid);

onSnapshot(userRef, (doc) => {
  console.log("User updated:", doc.data());
});
```

---

## Troubleshooting

### "firebase-service-account.json not found"
- Download the key from Firebase Console
- Place it in `backend/vignesh3d/firebase-service-account.json`
- Restart Django server

### "Firebase not initialized"
- Check that `firebase-service-account.json` path is correct
- Verify Firebase credentials are valid
- Check Django console for initialization errors

### "Invalid token"
- Token may be expired (valid for 1 hour)
- Ensure frontend is getting token from Firebase, not Django
- Check token format: should be JWT encoded

---

## Security Best Practices

✅ **DO:**
- Store service account key securely (`.gitignore`)
- Use Firestore security rules
- Validate all user inputs on backend
- Use HTTPS in production
- Regenerate keys periodically

❌ **DON'T:**
- Commit `firebase-service-account.json` to GitHub
- Expose API keys in frontend code (they're public by design)
- Trust client-side validation alone
- Use development keys in production

---

## Files Used

- `backend/vignesh3d/firebase_config.py` — Firebase setup & initialization
- `backend/firebase_views_examples.py` — Example API endpoints
- `backend/vignesh3d/firebase-service-account.json` — Service account key
- `.gitignore` — Prevents leaking API keys

---

## Examples

See `backend/firebase_views_examples.py` for ready-to-use Django views:
- ✓ Verify tokens
- ✓ Upload files
- ✓ Save/fetch user profiles
- ✓ Query Firestore
- ✓ Handle orders

---

## Support

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Admin SDK (Python)](https://firebase.google.com/docs/database/admin/start)
- [Firestore Best Practices](https://firebase.google.com/docs/firestore/best-practices)
