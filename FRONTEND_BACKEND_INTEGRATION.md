# Frontend-Backend Integration Guide

## Overview

The Pixels to Plastic (P2P) application now has a **unified API communication layer** that properly links frontend and backend operations.

## Architecture

```
Frontend (HTML/JS)
    ↓
API Client (api-client.js) ← Centralized
    ↓
Django REST API (Backend)
    ↓
Database (SQLite/Firebase)
```

---

## API Client Library (`frontend/api-client.js`)

A professional-grade JavaScript API client that handles:
- ✅ Automatic authentication with JWT tokens
- ✅ Request/response interceptors
- ✅ Centralized error handling
- ✅ Endpoint configuration management
- ✅ Event listeners for monitoring
- ✅ Timeout handling
- ✅ Auto-redirect on token expiration

### Global Functions

Available in all frontend pages:

```javascript
// API Configuration
API_CONFIG.BASE_URL          // 'http://localhost:8000/api'
API_CONFIG.AUTH.*            // Login, register, profile endpoints
API_CONFIG.PRODUCTS.*        // Product CRUD endpoints
API_CONFIG.CATEGORIES.*      // Category endpoints
API_CONFIG.ORDERS.*          // Order & payment endpoints
API_CONFIG.CART.*            // Shopping cart endpoints

// API Client
api.get(endpoint)            // GET request
api.post(endpoint, data)     // POST request  
api.patch(endpoint, data)    // PATCH request
api.put(endpoint, data)      // PUT request
api.delete(endpoint)         // DELETE request

// Authentication Helpers
isAuthenticated()            // Check if user is logged in
getCurrentUser()             // Get current user object
isAdmin()                    // Check if user is admin
logout()                     // Logout and redirect

// Error Handling
formatErrorMessage(error)    // Human-readable error messages
```

---

## File Updates

### Frontend Pages

#### 1. **admin-login.html**
- ✅ Imports `api-client.js`
- ✅ Uses `api.post()` for login/register
- ✅ Uses `API_CONFIG.AUTH.*` for endpoints
- ✅ Automatic token storage in localStorage

#### 2. **admin.html**  
- ✅ Imports `api-client.js`
- ✅ Auth guard using `isAuthenticated()` and `isAdmin()`
- ✅ All CRUD operations use new client:
  - `api.get()` for fetching data
  - `api.post()` for creating
  - `api.patch()` for updating
  - `api.delete()` for deleting
- ✅ Uses  `API_CONFIG` for all endpoints

#### 3. **index.html**
- ✅ Imports `api-client.js`
- ✅ Product loading and filtering
- ✅ Shopping cart operations
- ✅ Checkout & payment processing
- ✅ User authentication (login/register)
- ✅ Automatic error handling with `formatErrorMessage()`

---

## API Endpoints

### Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/login/` | User/admin login |
| POST | `/auth/register/` | Register new user |
| POST | `/auth/admin-register/` | Register as admin (requires key) |
| GET | `/auth/profile/` | Get user profile |
| POST | `/auth/refresh/` | Refresh JWT token |
| POST | `/auth/verify/` | Verify JWT token |

### Products
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/products/products/` | List all products |
| GET | `/products/products/{id}/` | Get product details |
| POST | `/products/products/` | Create product (admin) |
| PATCH | `/products/products/{id}/` | Update product (admin) |
| DELETE | `/products/products/{id}/` | Delete product (admin) |

### Categories
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/products/main-categories/` | List main categories |
| GET | `/products/categories/` | List subcategories |
| POST | `/products/categories/` | Create category (admin) |
| DELETE | `/products/categories/{id}/` | Delete category (admin) |

### Discounts
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/products/discounts/` | List discounts |
| POST | `/products/discounts/` | Create discount (admin) |
| DELETE | `/products/discounts/{id}/` | Delete discount (admin) |

### Shopping Cart
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/cart/` | Get cart contents |
| POST | `/cart/items/` | Add item to cart |
| PATCH | `/cart/items/{id}/` | Update cart item quantity |
| DELETE | `/cart/items/{id}/` | Remove item from cart |

### Orders
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/orders/` | List user's orders (admin sees all) |
| GET | `/orders/{id}/` | Get order details |
| POST | `/orders/checkout/` | Create order & payment |
| PATCH | `/orders/{id}/status/` | Update order status (admin) |
| POST | `/orders/payment/verify/` | Verify Razorpay payment |

---

## Request/Response Flow

### Login Example

**Frontend (index.html)**
```javascript
// User clicks "Login"
const res = await api.post(API_CONFIG.AUTH.LOGIN, {
  username: 'john',
  password: 'secret123'
});

// api-client.js automatically:
// 1. Adds Content-Type header
// 2. Converts data to JSON
// 3. Handles errors
// 4. Extracts response
```

**Backend (Django)**
```python
# POST /api/auth/login/
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "is_staff": false
  }
}
```

**Frontend Storage**
```javascript
// Automatically stored in localStorage
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
localStorage.getItem('user')

// Use for authenticated requests
api.post('/orders/', {...})  // Token added automatically
```

---

## Error Handling

### Automatic Error Handling

```javascript
try {
  const data = await api.get('/products/products/');
} catch (error) {
  // error is an APIError instance
  console.log(error.status);    // HTTP status
  console.log(error.message);   // Error message
  console.log(error.data);      // Response data
}
```

### User-Friendly Error Messages

```javascript
try {
  await api.post(API_CONFIG.AUTH.REGISTER, userData);
} catch (error) {
  // formatErrorMessage extracts first meaningful error
  const msg = formatErrorMessage(error);
  // "User with this username already exists"
  toast(msg, 'error');
}
```

---

## Authentication Flow

### Login & Token Management

1. **User Logs In**
   ```javascript
   const res = await api.post(API_CONFIG.AUTH.LOGIN, {username, password});
   localStorage.setItem('access_token', res.access);
   localStorage.setItem('user', JSON.stringify(res.user));
   ```

2. **API Client Sends Token**
   ```javascript
   // Automatically added to all requests
   headers: {
     'Authorization': 'Bearer <access_token>'
   }
   ```

3. **Token Expires (401)**
   ```javascript
   // api-client detects 401 status
   // Key is removed from localStorage
   // User redirected to login
   window.location.href = 'admin-login.html';
   ```

4. **Refresh Token** (if implemented)
   ```javascript
   // Can implement token refresh before expiration
   const newToken = await api.post(API_CONFIG.AUTH.REFRESH, {
     refresh: localStorage.getItem('refresh_token')
   });
   ```

---

## Admin Authentication Guard

### admin.html
```javascript
// Checks if user is logged in AND is admin
if (!isAuthenticated() || !isAdmin()) {
  window.location.href = 'admin-login.html';
}
```

### Getting Current User
```javascript
const user = getCurrentUser();
// Returns: {id, username, email, is_staff, first_name, last_name}
if (user && user.is_staff) {
  // User is admin
}
```

---

## CORS Configuration

Backend (`settings.py`) is configured with:
```python
INSTALLED_APPS = ['corsheaders', ...]
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', ...]
CORS_ALLOWED_ORIGINS = ['*']  # Allow all origins (dev only)
```

This allows frontend at `file://` or `http://localhost` to make requests to `http://localhost:8000`.

---

## Common Patterns

### Load Data on Page Open
```javascript
async function loadData() {
  try {
    const data = await api.get(API_CONFIG.PRODUCTS.LIST);
    const items = data.results || data;
    render Items(items);
  } catch (error) {
    toast(formatErrorMessage(error), 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadData);
```

### Create with Validation
```javascript
async function addProduct(formData) {
  try {
    const response = await api.post(API_CONFIG.PRODUCTS.LIST, formData);
    toast('✓ Product created', 'success');
    refreshList();
  } catch (error) {
    toast(formatErrorMessage(error), 'error');
  }
}
```

### Delete with Confirm
```javascript
async function deleteItem(id) {
  if (!confirm('Delete permanently?')) return;
  
  try {
    await api.delete(API_CONFIG.PRODUCTS.DELETE(id));
    toast('✓ Deleted', 'success');
    refreshList();
  } catch (error) {
    toast('Error: ' + error.message, 'error');
  }
}
```

### Progress Indication
```javascript
const btn = document.getElementById('submitBtn');
btn.disabled = true;
btn.textContent = 'Processing...';

try {
  await api.post('/endpoint/', data);
} finally {
  btn.disabled = false;
  btn.textContent = 'Submit';
}
```

---

## Server-Side Integration

For server-side Firebase operations, see [FIREBASE_SETUP.md](FIREBASE_SETUP.md).

### Backend Requirements
- ✅ Django REST Framework endpoints
- ✅ JWT authentication configured
- ✅ CORS headers enabled
- ✅ Proper error response format

---

## Debugging

### Monitor API Calls

```javascript
// Listen to all requests
api.on('request', (data) => {
  console.log('REQUEST:', data.url, data.options);
});

// Listen to responses
api.on('response', (data) => {
  console.log('RESPONSE:', data.status, data.data);
});

// Listen to errors
api.on('error', (error) => {
  console.log('ERROR:', error.message, error.data);
});

// Listen to 401 unauthorized
api.on('unauthorized', () => {
  console.log('Token expired, redirecting...');
});
```

### Check Network Tab
1. Open DevTools → Network tab
2. Perform action
3. Click request to inspect:
   - Headers sent
   - Request body
   - Response status
   - Response body

### Common Issues

**Problem**: Getting 401 Unauthorized
- **Solution**: Check `localStorage.getItem('access_token')` - it should have a valid JWT

**Problem**: CORS errors
- **Solution**: Backend CORS_ALLOWED_ORIGINS not configured properly

**Problem**: 404 Not Found
- **Solution**: Check API endpoint path matches Django URL patterns

**Problem**: "Cannot connect to server"
- **Solution**: Django server not running - start with `python manage.py runserver`

---

## Files Structure

```
frontend/
├── api-client.js          ← Main API client library
├── admin-login.html       ← Imports & uses api-client.js
├── admin.html             ← Imports & uses api-client.js
├── index.html             ← Imports & uses api-client.js
└── README.md

backend/
├── vignesh3d/
│   ├── settings.py        ← CORS configured
│   ├── urls.py            ← Main URL patterns
│   └── firebase_config.py ← Firebase Admin SDK
├── accounts/
│   ├── views.py           ← Login/Register endpoints
│   └── urls.py
├── products/
│   ├── views.py           ← Product CRUD endpoints
│   └── urls.py
├── cart/
│   ├── views.py           ← Cart endpoints
│   └── urls.py
├── orders/
│   ├── views.py           ← Checkout/Orders endpoints
│   └── urls.py
└── manage.py
```

---

## Next Steps

1. **Test Each Endpoint**
   - Use admin.html to create/edit products
   - Use index.html to shop and checkout
   - Monitor Network tab for API calls

2. **Add More Features**
   - Wishlist functionality
   - Product reviews & ratings
   - Order tracking
   - Email notifications

3. **Production Deployment**
   - Update `API_CONFIG.BASE_URL` to production URL
   - Add request rate limiting
   - Implement token refresh logic
   - Use HTTPS only
   - Set proper CORS_ALLOWED_ORIGINS

4. **Firebase Integration**
   - Authenticate users with Firebase
   - Store user profiles in Firestore
   - Upload product images to Storage
   - See [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

---

## Support

- Check console for error messages
- Use DevTools Network tab to inspect requests
- Test endpoints in Django admin: `http://localhost:8000/admin/`
- Review backend logs in terminal

Frontend and backend are now **properly integrated** and ready for development! 🚀
