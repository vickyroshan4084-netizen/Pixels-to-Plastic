from rest_framework import serializers
from .models import MainCategory, ProductCategory, Discount, Product, Promotion, PaymentMethod, SiteSettings


class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = MainCategory
        fields = ['id', 'name', 'description', 'icon', 'image', 'is_active']


class ProductCategorySerializer(serializers.ModelSerializer):
    main_category_name = serializers.ReadOnlyField()

    class Meta:
        model  = ProductCategory
        fields = ['id', 'main_category', 'main_category_name', 'name', 'description', 'base_price', 'image', 'is_active']


class DiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model  = Discount
        fields = ['id', 'name', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active', 'is_valid']


class ProductSerializer(serializers.ModelSerializer):
    image_display      = serializers.SerializerMethodField()
    in_stock           = serializers.ReadOnlyField()
    final_price        = serializers.ReadOnlyField()
    discount_amount    = serializers.ReadOnlyField()
    category_details   = ProductCategorySerializer(source='category', read_only=True)
    discount_details   = DiscountSerializer(source='discount', read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'title', 'description', 'price', 'final_price', 'discount_amount',
            'category', 'category_details', 'discount', 'discount_details',
            'image', 'image_url', 'image_display',
            'stock', 'in_stock', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_image_display(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.get_image()


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'banner_text', 'shipping_threshold', 'is_active', 'updated_at']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PaymentMethod
        fields = '__all__'


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SiteSettings
        fields = '__all__'
