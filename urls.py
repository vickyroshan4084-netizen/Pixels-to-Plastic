from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MainCategoryViewSet, ProductCategoryViewSet, DiscountViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'main-categories', MainCategoryViewSet, basename='main-category')
router.register(r'categories',      ProductCategoryViewSet, basename='category')
router.register(r'discounts',       DiscountViewSet, basename='discount')
router.register(r'products',        ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    # CSV export endpoint
    path('products/export_csv/', ProductViewSet.as_view({'get': 'export_csv'}), name='export-csv'),
]
