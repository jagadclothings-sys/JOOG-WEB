from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from coupons.models import Coupon
import secrets
import string

User = get_user_model()

class Influencer(models.Model):
    """Model to store influencer information and credentials"""
    
    # Basic Information
    name = models.CharField(max_length=200, help_text="Influencer's display name")
    email = models.EmailField(unique=True, help_text="Login email for the influencer")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    
    # Credentials
    username = models.CharField(max_length=50, unique=True, help_text="Unique username for login")
    api_key = models.CharField(max_length=64, unique=True, blank=True, help_text="API key for authentication")
    
    # Social Media Info (Optional)
    instagram_handle = models.CharField(max_length=100, blank=True, help_text="Instagram username without @")
    youtube_channel = models.CharField(max_length=100, blank=True, help_text="YouTube channel name")
    tiktok_handle = models.CharField(max_length=100, blank=True, help_text="TikTok username without @")
    website = models.URLField(blank=True, help_text="Personal website or blog")
    
    # Status and Settings
    is_active = models.BooleanField(default=True, help_text="Whether the influencer can access the dashboard")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
                                        help_text="Commission percentage (e.g., 5.00 for 5%)")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True, help_text="Last dashboard access")
    
    # Admin notes
    notes = models.TextField(blank=True, help_text="Internal admin notes about this influencer")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Influencer'
        verbose_name_plural = 'Influencers'
    
    def __str__(self):
        return f"{self.name} (@{self.username})"
    
    def save(self, *args, **kwargs):
        # Generate API key if not provided
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    def generate_api_key(self):
        """Generate a secure API key"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
    
    def regenerate_api_key(self):
        """Regenerate the API key (useful for security purposes)"""
        self.api_key = self.generate_api_key()
        self.save(update_fields=['api_key'])
        return self.api_key
    
    def get_assigned_coupons(self):
        """Get all coupons assigned to this influencer"""
        return self.coupons.filter(coupon__active=True)
    
    def get_total_orders(self):
        """Get total number of orders using influencer's coupons"""
        from orders.models import Order
        return Order.objects.filter(coupon__in=[ic.coupon for ic in self.get_assigned_coupons()]).count()
    
    def get_total_revenue(self):
        """Get total revenue generated from influencer's coupons"""
        from orders.models import Order
        from django.db.models import Sum
        coupons = [ic.coupon for ic in self.get_assigned_coupons()]
        result = Order.objects.filter(
            coupon__in=coupons,
            payment_status='completed'
        ).aggregate(total=Sum('final_amount'))
        return result['total'] or 0
    
    def get_commission_earned(self):
        """Calculate commission earned based on commission rate"""
        total_revenue = self.get_total_revenue()
        return (total_revenue * self.commission_rate) / 100
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])


class InfluencerCoupon(models.Model):
    """Link table between influencers and their assigned coupons"""
    
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='influencers')
    
    # Assignment details
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  help_text="Admin who assigned this coupon")
    
    # Performance tracking (optional)
    target_uses = models.PositiveIntegerField(null=True, blank=True, 
                                            help_text="Target number of coupon uses")
    notes = models.TextField(blank=True, help_text="Notes about this coupon assignment")
    
    class Meta:
        unique_together = ('influencer', 'coupon')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.influencer.name} - {self.coupon.code}"
    
    def get_usage_count(self):
        """Get number of times this coupon was used"""
        return self.coupon.used_count
    
    def get_orders_count(self):
        """Get number of orders using this coupon"""
        from orders.models import Order
        return Order.objects.filter(coupon=self.coupon).count()
    
    def get_revenue_generated(self):
        """Get revenue generated by this coupon"""
        from orders.models import Order
        from django.db.models import Sum
        result = Order.objects.filter(
            coupon=self.coupon,
            payment_status='completed'
        ).aggregate(total=Sum('final_amount'))
        return result['total'] or 0


class InfluencerLoginLog(models.Model):
    """Track influencer login attempts and sessions"""
    
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.influencer.username} - {status} - {self.login_time}"
