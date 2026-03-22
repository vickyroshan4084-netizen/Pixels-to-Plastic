from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MainCategory(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, blank=True, default='📦')
    image       = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Main Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='sub_categories')
    name          = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    base_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image         = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product Categories'
        unique_together = ['main_category', 'name']
        ordering = ['main_category', 'name']

    def __str__(self):
        return f"{self.main_category.name} > {self.name}"

    @property
    def main_category_name(self):
        return self.main_category.name


class Discount(models.Model):
    DISCOUNT_TYPES = [('percentage', 'Percentage %'), ('fixed', 'Fixed Amount ₹')]
    name           = models.CharField(max_length=100, unique=True)
    discount_type  = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date     = models.DateTimeField(null=True, blank=True)
    end_date       = models.DateTimeField(null=True, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        val = f"{self.discount_value}%" if self.discount_type == 'percentage' else f"₹{self.discount_value}"
        return f"{self.name} ({val})"

    @property
    def is_valid(self):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class Product(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    discount    = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image       = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url   = models.URLField(blank=True)
    stock       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def discount_amount(self):
        if not self.discount or not self.discount.is_valid:
            return 0
        if self.discount.discount_type == 'percentage':
            return round(float(self.price) * float(self.discount.discount_value) / 100, 2)
        return min(float(self.discount.discount_value), float(self.price))

    @property
    def final_price(self):
        return round(float(self.price) - self.discount_amount, 2)


    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url or 'https://placehold.co/400x300/2e2e2e/ff6f61?text=P2P'


class Promotion(models.Model):
    banner_text        = models.CharField(max_length=255, default="🎉 Buy 1 Get 2 Free | Free shipping on orders above ₹1,000")
    shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    is_active          = models.BooleanField(default=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Promotion: {self.banner_text[:30]}..."


class PaymentMethod(models.Model):
    METHOD_TYPES = [
        ('gateway', 'Payment Gateway (Razorpay)'),
        ('upi',     'Direct UPI (QR Code)'),
        ('cod',     'Cash on Delivery'),
    ]
    name         = models.CharField(max_length=100)
    method_type  = models.CharField(max_length=20, choices=METHOD_TYPES, default='upi')
    icon         = models.CharField(max_length=20, blank=True, default='💳')
    qr_code      = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    upi_id       = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True, help_text="Instructions for the customer")
    is_active    = models.BooleanField(default=True)
    order        = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"


class SiteSettings(models.Model):
    about_title     = models.CharField(max_length=200, default="About Pixels to Plastic")
    about_text      = models.TextField(default="Crafted with Precision in India. Miniatures, tools and home décor — each piece uniquely printed to order.")
    contact_email   = models.EmailField(default="contact@p2p.com")
    contact_phone   = models.CharField(max_length=20, default="+91 98765 43210")
    contact_address = models.TextField(default="Chennai, Tamil Nadu, India")
    footer_copy     = models.CharField(max_length=255, default="© 2026 Pixels to Plastic (P2P) | Crafted with Precision in India")
    is_active       = models.BooleanField(default=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f"Site Settings (Updated: {self.updated_at.strftime('%Y-%m-%d')})"
