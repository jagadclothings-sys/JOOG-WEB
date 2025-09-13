from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'minimum_amount', 'used_count', 'max_uses', 'active', 'valid_from', 'valid_to']
    list_filter = ['discount_type', 'active', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['used_count', 'created_at']
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'discount_type', 'discount_value', 'minimum_amount')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'used_count')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )