from django.db import models


class MainCategory(models.Model):
    name = models.CharField(max_length=100)
    # ✅ Changed from CharField to ImageField — saves to media/images/categories/
    icon = models.ImageField(upload_to='images/categories/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Main Categories'


class ProductCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subcategories')
    name          = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    base_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active     = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.main_category.name} › {self.name}'

    class Meta:
        verbose_name_plural = 'Product Categories'


class Discount(models.Model):
    DISCOUNT_TYPES = [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]
    name           = models.CharField(max_length=100)
    discount_type  = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date     = models.DateTimeField(blank=True, null=True)
    end_date       = models.DateTimeField(blank=True, null=True)
    is_active      = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class Product(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    # ✅ Changed from URLField to ImageField — saves to media/images/products/
    image       = models.ImageField(upload_to='images/products/', blank=True, null=True)
    category    = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    discount    = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    stock       = models.IntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        if self.discount and self.discount.is_valid:
            if self.discount.discount_type == 'percentage':
                return float(self.price) * (1 - float(self.discount.discount_value) / 100)
            else:
                return max(0, float(self.price) - float(self.discount.discount_value))
        return float(self.price)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return ''
