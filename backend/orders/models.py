from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('paid',       'Paid'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]
    user               = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Shipping details
    guest_name         = models.CharField(max_length=200)
    guest_email        = models.EmailField()
    guest_phone        = models.CharField(max_length=20)
    shipping_address   = models.TextField()
    city               = models.CharField(max_length=100)
    state              = models.CharField(max_length=100)
    pincode            = models.CharField(max_length=10)
    # Payment
    payment_method     = models.CharField(max_length=50, default='cod')
    razorpay_order_id  = models.CharField(max_length=200, blank=True)
    razorpay_payment_id= models.CharField(max_length=200, blank=True)
    payment_verified   = models.BooleanField(default=False)
    # Totals
    subtotal           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_charge    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total              = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Status
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.guest_name} ({self.status})"


class OrderItem(models.Model):
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product     = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    title       = models.CharField(max_length=200)  # snapshot
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)
    quantity    = models.PositiveIntegerField(default=1)
    line_total  = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.title}"
