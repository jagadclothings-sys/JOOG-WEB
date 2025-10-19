from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from coupons.models import Coupon

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=3, choices=[('S','S'),('M','M'),('L','L'),('XL','XL'),('XXL','XXL')], default='M', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional combo linkage for grouped combo purchases
    combo = models.ForeignKey('products.Combo', on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_items')
    combo_group = models.CharField(max_length=36, null=True, blank=True, help_text="UUID to group items belonging to one combo instance")
    
    class Meta:
        unique_together = ('cart', 'product', 'size')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.size})"
    
    def get_total_price(self):
        return self.quantity * self.product.price

class CartCombo(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='combos')
    combo = models.ForeignKey('products.Combo', on_delete=models.CASCADE)
    combo_group = models.CharField(max_length=36, help_text='UUID identifying this combo instance in the cart')
    original_total = models.DecimalField(max_digits=10, decimal_places=2)
    combo_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['combo_group']),
        ]

    def __str__(self):
        return f"{self.combo.name} in cart ({self.discount_amount} off)"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=25, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Shipping information - keep both for backward compatibility and flexibility
    selected_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, default='')
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
# Payment information
    payment_method = models.CharField(max_length=50, default='phonepe')
    payment_status = models.CharField(max_length=20, default='pending')
    # PhonePe specific fields
    phonepe_merchant_txn_id = models.CharField(max_length=64, blank=True)
    phonepe_txn_id = models.CharField(max_length=128, blank=True)
    phonepe_meta = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email tracking fields
    confirmation_email_sent = models.BooleanField(default=False, help_text="Order confirmation email sent")
    confirmation_email_sent_at = models.DateTimeField(null=True, blank=True, help_text="When confirmation email was sent")
    confirmation_email_error = models.TextField(blank=True, help_text="Error message if confirmation email failed")
    
    invoice_email_sent = models.BooleanField(default=False, help_text="Invoice email sent")
    invoice_email_sent_at = models.DateTimeField(null=True, blank=True, help_text="When invoice email was sent")
    invoice_email_error = models.TextField(blank=True, help_text="Error message if invoice email failed")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
    
    def _generate_order_number(self):
        from django.utils import timezone
        from django.db.models import Max
        import re
        
        today = timezone.now()
        date_str = today.strftime("%Y%m%d")
        
        # Get the highest order number for today
        pattern = f"JOOG-{date_str}-"
        today_orders = Order.objects.filter(
            order_number__startswith=pattern
        ).aggregate(max_num=Max('order_number'))
        
        if today_orders['max_num']:
            # Extract the counter from the last order number
            last_order = today_orders['max_num']
            match = re.search(r'JOOG-\d{8}-(\d{4})', last_order)
            if match:
                counter = int(match.group(1)) + 1
            else:
                counter = 1
        else:
            counter = 1
        
        return f"JOOG-{date_str}-{counter:04d}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=3, choices=[('S','S'),('M','M'),('L','L'),('XL','XL'),('XXL','XXL')], default='M', blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.size})"
    
    def get_total_price(self):
        return self.quantity * self.price
    
    @property
    def base_price(self):
        """Calculate base price without tax (total price excluding tax)"""
        total_with_tax = self.get_total_price()
        tax_rate = getattr(self.product, 'tax_percentage', 5.0) / 100
        base_amount = total_with_tax / (1 + tax_rate)
        return base_amount
    
    @property
    def tax_amount(self):
        """Calculate tax amount for this item"""
        return self.get_total_price() - self.base_price
