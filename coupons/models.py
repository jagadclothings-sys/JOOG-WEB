from django.db import models
from django.utils import timezone
from decimal import Decimal

class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        now = timezone.now()
        if not self.active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True
    
    def get_discount_amount(self, order_total):
        if order_total < self.minimum_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            return (order_total * self.discount_value) / 100
        else:
            return min(self.discount_value, order_total)
    
    def apply_coupon(self):
        """Increment the usage count of the coupon"""
        self.used_count += 1
        self.save(update_fields=['used_count'])