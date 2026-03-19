# ============================================================
# ADD THESE LINES to the bottom of backend/vignesh3d/settings.py
# ============================================================

import os

# Media files — uploaded images saved here locally
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Make sure these are in INSTALLED_APPS (already there, just confirming):
# 'rest_framework',
# 'corsheaders',
# 'products',
# 'accounts',
# 'cart',
# 'orders',

# Make sure this is in MIDDLEWARE (already there):
# 'corsheaders.middleware.CorsMiddleware',

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework — allow multipart uploads
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',   # ✅ for image uploads
        'rest_framework.parsers.FormParser',         # ✅ for form data
        'rest_framework.parsers.JSONParser',         # ✅ for JSON
    ],
}
