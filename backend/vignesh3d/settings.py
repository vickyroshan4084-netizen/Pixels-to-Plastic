"""
backend/vignesh3d/settings.py
─────────────────────────────────────────────────────────────────────────────
Works for LOCAL (SQLite, DEBUG=True) and RENDER.COM (PostgreSQL, DEBUG=False).
No changes needed when switching — environment variables control everything.
─────────────────────────────────────────────────────────────────────────────
"""
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Firebase (optional) ───────────────────────────────────────────────────────
try:
    from .firebase_config import initialize_firebase
    initialize_firebase()
except Exception as e:
    print(f"Warning: Firebase init skipped: {e}")

# ── Core settings ─────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-p2p-local-dev-key-change-in-production-xyz987abc'
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Locally: allow all. On Render: locked to actual hostnames.
ALLOWED_HOSTS = ['*']
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
if _render_host:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', _render_host, '.onrender.com', '.vercel.app']

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',  # must be before django.contrib.staticfiles
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'accounts',
    'products',
    'cart',
    'orders',
]

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # MUST be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF     = 'vignesh3d.urls'
WSGI_APPLICATION = 'vignesh3d.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

# ── Database ──────────────────────────────────────────────────────────────────
# LOCAL  → SQLite (automatic, zero setup)
# RENDER → PostgreSQL (Render auto-sets DATABASE_URL when you add a DB)
_db_url = os.environ.get('DATABASE_URL', 'postgresql://p2p_shop_user:Tn1C6kbjuEYxDmMHFGeG7yLh7QNzLWoM@dpg-d700qfk50q8c739tssg0-a/p2p_shop')
if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(_db_url, conn_max_age=600, conn_health_checks=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':   BASE_DIR / 'db.sqlite3',
        }
    }

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS  = True   # allows Vercel + any other frontend
CORS_ALLOW_CREDENTIALS  = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization',
    'content-type', 'dnt', 'origin', 'user-agent',
    'x-csrftoken', 'x-requested-with',
]

# ── REST Framework + JWT ──────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':    timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES':        ('Bearer',),
}

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Misc ──────────────────────────────────────────────────────────────────────
LANGUAGE_CODE      = 'en-us'
TIME_ZONE          = 'Asia/Kolkata'
USE_I18N           = True
USE_TZ             = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_ENGINE     = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 604800  # 7 days

EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Pixels to Plastic <no-reply@pixelstoplastic.com>'

# ── Payment keys (set in Render Environment Variables) ────────────────────────
RAZORPAY_KEY_ID     = os.environ.get('RAZORPAY_KEY_ID',     'rzp_test_YOUR_KEY_ID_HERE')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'YOUR_RAZORPAY_SECRET_HERE')
GPAY_UPI_VPA        = os.environ.get('GPAY_UPI_VPA',        'your-upi-id@okaxis')
GPAY_MERCHANT_NAME  = 'Pixels to Plastic'

# ── Admin registration key ────────────────────────────────────────────────────
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'p2p_admin_2024')
