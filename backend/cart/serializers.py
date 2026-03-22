from rest_framework import serializers
from products.serializers import ProductSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product    = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model  = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'line_total']

    def validate_product_id(self, value):
        from products.models import Product
        try:
            p = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        if not p.in_stock:
            raise serializers.ValidationError("Product is out of stock.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items      = CartItemSerializer(many=True, read_only=True)
    total      = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()

    class Meta:
        model  = Cart
        fields = ['id', 'items', 'total', 'item_count']
