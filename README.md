# Pixels to Plastic (P2P) — Local Development

## Quick Start

### Windows
Double-click: `run_windows.bat`

### Mac / Linux
```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

---

## What the script does
1. Installs all Python packages
2. Creates the SQLite database (no setup needed)
3. Seeds sample categories
4. Prompts you to create an admin account
5. Starts the server at http://localhost:8000

---

## Open the Website
- **Shop:**          Open `frontend/index.html` in your browser  
- **Admin panel:**   Open `frontend/admin.html` in your browser  
- **Admin login:**   Open `frontend/admin-login.html`  
- **Django admin:**  http://localhost:8000/admin/

---

## Add Your Payment Keys

Open `backend/vignesh3d/settings.py` and fill in:

```python
# Razorpay — get FREE test keys at dashboard.razorpay.com
RAZORPAY_KEY_ID     = 'rzp_test_YOUR_KEY_ID_HERE'
RAZORPAY_KEY_SECRET = 'YOUR_RAZORPAY_SECRET_HERE'

# Google Pay — your UPI ID from GPay / PhonePe / Paytm profile
GPAY_UPI_VPA = 'your-upi-id@okaxis'
```

---

## Firebase Setup (Server-side)

Firebase Admin SDK is integrated for server-side operations like user authentication, Firestore database, and Cloud Storage.

### Step 1: Download Service Account Key
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select project: **pixal-to-plastic**
3. Settings → Service Accounts → Generate New Private Key
4. Save as `firebase-service-account.json`

### Step 2: Place the Key in Backend
```
backend/vignesh3d/firebase-service-account.json
```

### Step 3: Use Firebase in Your Views
```python
from vignesh3d.firebase_config import get_auth, get_firestore, get_storage

# Verify token from frontend
decoded_token = get_auth().verify_id_token(token)

# Get data from Firestore
db = get_firestore()
doc = db.collection('users').document(user_id).get()

# Upload files to Storage
bucket = get_storage()
blob = bucket.blob(f'photos/{user_id}.jpg')
blob.upload_from_string(file_data)
```

**Note:** Add `firebase-service-account.json` to `.gitignore` — never commit API keys!

---

## Admin Registration Key
Default key to register as admin: `p2p_admin_2024`  
(Change it in `backend/accounts/serializers.py` → `ADMIN_KEY`)

---

## API Endpoints
| Method | URL | What it does |
|--------|-----|-------------|
| POST | /api/auth/login/ | Login |
| POST | /api/auth/register/ | Register user |
| POST | /api/auth/admin-register/ | Register admin |
| GET | /api/products/products/ | List products |
| GET | /api/products/categories/ | List categories |
| GET | /api/cart/ | View cart |
| POST | /api/cart/items/ | Add to cart |
| POST | /api/orders/checkout/ | Place order |
| POST | /api/orders/payment/verify/ | Verify Razorpay payment |
