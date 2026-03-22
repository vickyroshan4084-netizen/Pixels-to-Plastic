from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = ['id', 'title', 'unit_price', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'guest_name', 'guest_email', 'guest_phone',
            'shipping_address', 'city', 'state', 'pincode',
            'payment_method', 'razorpay_order_id', 'payment_verified',
            'subtotal', 'shipping_charge', 'total',
            'status', 'created_at', 'items',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'razorpay_order_id', 'payment_verified']
