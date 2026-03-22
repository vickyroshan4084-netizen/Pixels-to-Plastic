from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'guest_name', 'guest_email', 'total', 'payment_method', 'status', 'created_at']
    list_filter   = ['status', 'payment_method']
    search_fields = ['guest_name', 'guest_email', 'guest_phone']
    list_editable = ['status']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'payment_verified']
    inlines = [OrderItemInline]
