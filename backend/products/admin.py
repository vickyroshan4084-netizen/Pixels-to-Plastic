from django.contrib import admin
from .models import MainCategory, ProductCategory, Discount, Product, Promotion, PaymentMethod, SiteSettings

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method_type', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['banner_text', 'shipping_threshold', 'is_active', 'updated_at']
    list_editable = ['is_active', 'shipping_threshold']
@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    list_editable = ['is_active']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['about_title', 'contact_email', 'contact_phone', 'is_active', 'updated_at']
    list_editable = ['is_active']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display  = ['main_category', 'name', 'base_price', 'is_active']
    list_filter   = ['main_category']
    list_editable = ['is_active']

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display  = ['name', 'discount_type', 'discount_value', 'is_active', 'is_valid']
    list_editable = ['is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'price', 'final_price', 'stock', 'is_active']
    list_filter   = ['category__main_category', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['price', 'stock', 'is_active']
