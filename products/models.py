from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    tax_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=18.00, 
        help_text="Default GST tax rate for all products in this category (e.g., 18.00 for 18%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})
    
    def update_products_tax_rate(self):
        """Update tax percentage for all products in this category"""
        updated_count = self.products.update(tax_percentage=self.tax_percentage)
        return updated_count
    
    def save(self, *args, **kwargs):
        # Check if tax_percentage has changed
        update_products = False
        if self.pk:
            try:
                old_instance = Category.objects.get(pk=self.pk)
                if old_instance.tax_percentage != self.tax_percentage:
                    update_products = True
            except Category.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Update all products in this category if tax rate changed
        if update_products:
            self.update_products_tax_rate()

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/')
    # legacy single-stock field kept so existing views/forms work; not used for size inventory
    stock = models.PositiveIntegerField(default=0)
    # aggregate_stock kept for legacy; real stock lives in ProductStock
    # Obsolete aggregate stock field kept for backward compatibility; not used for per-size stock checks
    aggregate_stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    hsn_code = models.CharField(max_length=10, blank=True, null=True, help_text="HSN (Harmonized System of Nomenclature) code for GST")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="GST tax rate for this product (e.g., 18.00 for 18%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def total_stock(self):
        # Sum quantity across all size rows
        return sum(s.quantity for s in self.size_stocks.all())

    def is_in_stock(self):
        return self.total_stock() > 0 and self.available
    
    def get_stock_status(self):
        if not self.available:
            return "Unavailable"
        elif self.stock == 0:
            return "Out of Stock"
        elif self.stock <= 5:
            return f"Only {self.stock} left"
        else:
            return "In Stock"
    
    def save(self, *args, **kwargs):
        # If this is a new product and no tax_percentage is set, inherit from category
        if not self.pk and self.category and self.tax_percentage == 18.00:  # 18.00 is the default
            self.tax_percentage = self.category.tax_percentage
        super().save(*args, **kwargs)


class ProductStock(models.Model):
    SIZE_CHOICES = [
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
    ]

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='size_stocks')
    size = models.CharField(max_length=3, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.quantity})"

    def in_stock(self):
        return self.quantity > 0 and self.product.available

    def decrease(self, qty):
        if qty <= self.quantity:
            self.quantity -= qty
            self.save()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class ContactRequest(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('order', 'Order Support'),
        ('return', 'Returns & Exchanges'),
        ('shipping', 'Shipping Questions'),
        ('product', 'Product Information'),
        ('feedback', 'Feedback'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin use")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Request'
        verbose_name_plural = 'Contact Requests'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_subject_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'in_progress': 'bg-blue-100 text-blue-800',
            'resolved': 'bg-green-100 text-green-800',
            'closed': 'bg-gray-100 text-gray-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')


class Combo(models.Model):
    """A combo/bundle made up of multiple products."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='combos/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Fixed combo price")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:combo_detail', kwargs={'slug': self.slug})

    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class ComboItem(models.Model):
    """Links a product to a combo with a quantity."""
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('combo', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.combo.name}"


class ComboImage(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='combos/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.combo.name}"


class BannerImage(models.Model):
    """
    Home page banner slide. Admin can upload multiple slides.
    """
    image = models.ImageField(upload_to='banners/')
    title = models.CharField(max_length=150, blank=True)
    subtitle = models.CharField(max_length=250, blank=True)
    link_url = models.URLField(blank=True, help_text="Optional: clicking the banner opens this link")
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Home Banner Image'
        verbose_name_plural = 'Home Banner Images'

    def __str__(self):
        return self.title or f"Banner #{self.pk}"
