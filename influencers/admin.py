from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Influencer, InfluencerCoupon, InfluencerLoginLog

@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ['name', 'username', 'email', 'is_active', 'commission_rate', 
                   'total_coupons', 'total_orders', 'total_revenue', 'last_login', 'created_at']
    list_filter = ['is_active', 'created_at', 'last_login', 'commission_rate']
    search_fields = ['name', 'username', 'email', 'instagram_handle', 'youtube_channel']
    readonly_fields = ['api_key', 'created_at', 'updated_at', 'last_login', 
                      'get_dashboard_url', 'get_credentials_info']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'username')
        }),
        ('Social Media', {
            'fields': ('instagram_handle', 'youtube_channel', 'tiktok_handle', 'website'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'commission_rate')
        }),
        ('Credentials & Access', {
            'fields': ('api_key', 'get_dashboard_url', 'get_credentials_info'),
            'classes': ('wide',)
        }),
        ('Tracking', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
        ('Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['regenerate_api_keys', 'activate_influencers', 'deactivate_influencers']
    
    def total_coupons(self, obj):
        """Display total number of assigned coupons"""
        count = obj.coupons.count()
        if count > 0:
            return format_html('<strong style="color: #0066cc;">{}</strong>', count)
        return 0
    total_coupons.short_description = 'Coupons'
    
    def total_orders(self, obj):
        """Display total orders using influencer's coupons"""
        count = obj.get_total_orders()
        return format_html('<strong style="color: #0066cc;">{}</strong>', count)
    total_orders.short_description = 'Orders'
    
    def total_revenue(self, obj):
        """Display total revenue generated"""
        revenue = obj.get_total_revenue()
        return format_html('<strong style="color: #00aa00;">₹{:,.2f}</strong>', revenue)
    total_revenue.short_description = 'Revenue'
    
    def get_dashboard_url(self, obj):
        """Generate dashboard URL for the influencer"""
        if obj.pk:
            # This will be the URL where influencers can login
            url = f"/influencers/dashboard/?username={obj.username}&api_key={obj.api_key}"
            return format_html(
                '<a href="{}" target="_blank" style="color: #0066cc; font-weight: bold;">📊 Dashboard Link</a><br>'
                '<small style="color: #666;">Share this link with the influencer</small>',
                url
            )
        return "Save to generate dashboard URL"
    get_dashboard_url.short_description = 'Dashboard Access'
    
    def get_credentials_info(self, obj):
        """Display credentials information"""
        if obj.pk:
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
                '<strong>Login Credentials:</strong><br>'
                'Username: <code>{}</code><br>'
                'API Key: <code style="font-size: 10px;">{}</code><br>'
                '</div>',
                obj.username, obj.api_key
            )
        return "Save to generate credentials"
    get_credentials_info.short_description = 'Login Credentials'
    
    def regenerate_api_keys(self, request, queryset):
        """Admin action to regenerate API keys"""
        count = 0
        for influencer in queryset:
            influencer.regenerate_api_key()
            count += 1
        self.message_user(request, f'Successfully regenerated API keys for {count} influencer(s).')
    regenerate_api_keys.short_description = "🔄 Regenerate API Keys"
    
    def activate_influencers(self, request, queryset):
        """Admin action to activate influencers"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {count} influencer(s).')
    activate_influencers.short_description = "✅ Activate selected influencers"
    
    def deactivate_influencers(self, request, queryset):
        """Admin action to deactivate influencers"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {count} influencer(s).')
    deactivate_influencers.short_description = "❌ Deactivate selected influencers"


@admin.register(InfluencerCoupon)
class InfluencerCouponAdmin(admin.ModelAdmin):
    list_display = ['influencer', 'coupon_code', 'coupon_discount', 'usage_count', 
                   'orders_count', 'revenue_generated', 'assigned_at', 'assigned_by']
    list_filter = ['assigned_at', 'coupon__active', 'coupon__discount_type']
    search_fields = ['influencer__name', 'influencer__username', 'coupon__code']
    raw_id_fields = ['influencer', 'coupon', 'assigned_by']
    readonly_fields = ['assigned_at', 'get_performance_stats']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('influencer', 'coupon', 'assigned_by')
        }),
        ('Tracking', {
            'fields': ('target_uses', 'assigned_at', 'get_performance_stats'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def coupon_code(self, obj):
        """Display coupon code with link"""
        return format_html(
            '<strong style="color: #0066cc;">{}</strong>',
            obj.coupon.code
        )
    coupon_code.short_description = 'Coupon Code'
    
    def coupon_discount(self, obj):
        """Display coupon discount"""
        if obj.coupon.discount_type == 'percentage':
            return f"{obj.coupon.discount_value}%"
        else:
            return f"₹{obj.coupon.discount_value}"
    coupon_discount.short_description = 'Discount'
    
    def usage_count(self, obj):
        """Display usage count"""
        count = obj.get_usage_count()
        max_uses = obj.coupon.max_uses
        if max_uses:
            return format_html('{} / {}', count, max_uses)
        return count
    usage_count.short_description = 'Uses'
    
    def orders_count(self, obj):
        """Display orders count"""
        count = obj.get_orders_count()
        return format_html('<strong>{}</strong>', count)
    orders_count.short_description = 'Orders'
    
    def revenue_generated(self, obj):
        """Display revenue generated"""
        revenue = obj.get_revenue_generated()
        return format_html('<strong style="color: #00aa00;">₹{:,.2f}</strong>', revenue)
    revenue_generated.short_description = 'Revenue'
    
    def get_performance_stats(self, obj):
        """Display performance statistics"""
        if obj.pk:
            usage = obj.get_usage_count()
            orders = obj.get_orders_count()
            revenue = obj.get_revenue_generated()
            
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
                '<strong>Performance Stats:</strong><br>'
                'Total Uses: <strong>{}</strong><br>'
                'Total Orders: <strong>{}</strong><br>'
                'Revenue Generated: <strong style="color: #00aa00;">₹{:,.2f}</strong><br>'
                '</div>',
                usage, orders, revenue
            )
        return "Save to view performance stats"
    get_performance_stats.short_description = 'Performance'


@admin.register(InfluencerLoginLog)
class InfluencerLoginLogAdmin(admin.ModelAdmin):
    list_display = ['influencer', 'login_time', 'success', 'ip_address', 'get_user_agent']
    list_filter = ['success', 'login_time', 'influencer']
    search_fields = ['influencer__name', 'influencer__username', 'ip_address']
    readonly_fields = ['influencer', 'login_time', 'ip_address', 'user_agent', 'success']
    
    def has_add_permission(self, request):
        """Disable adding login logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make login logs read-only"""
        return False
    
    def get_user_agent(self, obj):
        """Display shortened user agent"""
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    get_user_agent.short_description = 'User Agent'
