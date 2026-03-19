from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .models import MainCategory, ProductCategory, Discount, Product
from .serializers import (
    MainCategorySerializer, ProductCategorySerializer,
    DiscountSerializer, ProductSerializer
)
import csv
from django.http import HttpResponse


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class MainCategoryViewSet(viewsets.ModelViewSet):
    queryset           = MainCategory.objects.all()
    serializer_class   = MainCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    # ✅ Accept multipart/form-data so image files can be uploaded
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        return {'request': self.request}


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset           = ProductCategory.objects.select_related('main_category').filter(is_active=True)
    serializer_class   = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = ProductCategory.objects.select_related('main_category').all()
        main = self.request.query_params.get('main_category')
        if main:
            qs = qs.filter(main_category=main)
        return qs


class DiscountViewSet(viewsets.ModelViewSet):
    queryset           = Discount.objects.all()
    serializer_class   = DiscountSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset           = Product.objects.select_related('category', 'discount').filter(is_active=True)
    serializer_class   = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    # ✅ Accept multipart/form-data so image files can be uploaded
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'category__main_category', 'discount').filter(is_active=True)
        category = self.request.query_params.get('category')
        search   = self.request.query_params.get('search')
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def export_csv(self, request):
        """Export all products as CSV file"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="p2p_products.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Category', 'Price', 'Final Price', 'Stock', 'Image URL'])
        for p in self.get_queryset():
            writer.writerow([p.id, p.title, p.category.name if p.category else '', p.price, p.final_price, p.stock, p.image_url])
        return response
