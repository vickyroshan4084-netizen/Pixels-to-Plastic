from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MainCategoryViewSet, ProductCategoryViewSet, DiscountViewSet, 
    ProductViewSet, PromotionViewSet, PaymentMethodViewSet, SiteSettingsViewSet
)

router = DefaultRouter()
router.register('main-categories', MainCategoryViewSet, basename='main-category')
router.register('categories',      ProductCategoryViewSet, basename='category')
router.register('discounts',       DiscountViewSet, basename='discount')
router.register('products',        ProductViewSet, basename='product')
router.register('promotions',      PromotionViewSet, basename='promotion')
router.register('payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register('settings', SiteSettingsViewSet, basename='site-settings')

urlpatterns = [path('', include(router.urls))]
