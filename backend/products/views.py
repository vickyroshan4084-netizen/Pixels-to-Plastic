import csv
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MainCategory, ProductCategory, Discount, Product, Promotion, PaymentMethod, SiteSettings
from .serializers import (
    MainCategorySerializer, ProductCategorySerializer,
    DiscountSerializer, ProductSerializer, PromotionSerializer,
    PaymentMethodSerializer, SiteSettingsSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class MainCategoryViewSet(viewsets.ModelViewSet):
    queryset = MainCategory.objects.filter(is_active=True)
    serializer_class = MainCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.filter(is_active=True).select_related('main_category')
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['main_category']


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    search_fields    = ['title', 'description']
    ordering_fields  = ['price', 'created_at', 'title']
    ordering         = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.select_related('category__main_category', 'discount')
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)

        # filter by main category name
        main_cat = self.request.query_params.get('main_category')
        if main_cat:
            qs = qs.filter(category__main_category__name__icontains=main_cat)

        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="p2p_products.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Category', 'Price', 'Discount', 'Final Price', 'Stock', 'Active', 'Date'])
        for p in Product.objects.select_related('category', 'discount'):
            writer.writerow([
                p.id, p.title,
                str(p.category) if p.category else '',
                p.price,
                str(p.discount) if p.discount else 'None',
                p.final_price, p.stock, p.is_active,
                p.created_at.strftime('%d/%m/%Y')
            ])
        return response

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        return self.export_csv(request)


class PromotionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        promo = self.get_queryset().first()
        if promo:
            return Response(self.get_serializer(promo).data)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer


class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteSettings.objects.filter(is_active=True)
    serializer_class = SiteSettingsSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        settings = self.queryset.first()
        if not settings:
            # Create a default one if none exists
            settings = SiteSettings.objects.create()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    permission_classes = [permissions.AllowAny]
