from rest_framework import serializers
from .models import MainCategory, ProductCategory, Discount, Product


class MainCategorySerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model  = MainCategory
        fields = ['id', 'name', 'icon', 'icon_url']

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        if obj.icon:
            return obj.icon.url
        return ''

    # Accept both icon (file) field on write
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Return icon as the URL so frontend can display it
        data['icon'] = self.get_icon_url(instance)
        return data


class ProductCategorySerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)

    class Meta:
        model  = ProductCategory
        fields = ['id', 'main_category', 'main_category_name', 'name', 'description', 'base_price', 'is_active']


class DiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Discount
        fields = ['id', 'name', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active', 'is_valid']


class ProductSerializer(serializers.ModelSerializer):
    final_price        = serializers.FloatField(read_only=True)
    image_url          = serializers.SerializerMethodField()
    category_name      = serializers.CharField(source='category.name', read_only=True)
    category_details   = ProductCategorySerializer(source='category', read_only=True)
    main_category_name = serializers.CharField(source='category.main_category.name', read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'title', 'description', 'price', 'final_price',
            'image', 'image_url', 'category', 'category_name',
            'category_details', 'main_category_name',
            'discount', 'stock', 'is_active', 'created_at',
        ]
        extra_kwargs = {'image': {'required': False}}

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return ''
