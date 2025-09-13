from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect

class CustomAdminSite(AdminSite):
    site_header = "JOOG Admin"
    site_title = "JOOG Admin Portal"
    index_title = "Welcome to JOOG Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.custom_index), name='index'),
        ]
        return custom_urls + urls
    
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def custom_index(self, request):
        """Custom admin index that redirects to our custom dashboard"""
        if request.user.is_staff:
            return HttpResponseRedirect('/admin-dashboard/')
        else:
            return HttpResponseRedirect('/admin/login/')

# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with custom admin site
from products.models import Category, Product, ProductImage, Review
from accounts.models import CustomUser
from orders.models import Order, OrderItem
from coupons.models import Coupon

@admin.register(Category, site=custom_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product, site=custom_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created_at']
    list_filter = ['available', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'available']
    inlines = [ProductImageInline]

@admin.register(Review, site=custom_admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']

@admin.register(CustomUser, site=custom_admin_site)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(Order, site=custom_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']

@admin.register(Coupon, site=custom_admin_site)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active']
    list_filter = ['active', 'discount_type', 'valid_from', 'valid_to']
    search_fields = ['code']
