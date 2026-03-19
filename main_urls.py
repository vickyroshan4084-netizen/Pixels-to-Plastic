# ============================================================
# backend/vignesh3d/urls.py — REPLACE your current urls.py with this
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # ✅ serves media files

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',     include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/cart/',     include('cart.urls')),
    path('api/orders/',   include('orders.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ✅ This line makes Django serve uploaded images at /media/images/...
