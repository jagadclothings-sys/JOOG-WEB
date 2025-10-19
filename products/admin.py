from django.contrib import admin
from .models import Category, Product, ProductImage, ProductStock, Review, ContactRequest, BannerImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tax_percentage', 'product_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_editable = ['tax_percentage']
    list_filter = ['tax_percentage', 'created_at']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Tax Configuration', {
            'fields': ('tax_percentage',),
            'description': (
                'Set the default GST tax rate for this category. '
                'All existing products in this category will be updated '
                'to use this tax rate when you save changes.'
            )
        }),
    )
    
    def product_count(self, obj):
        """Display number of products in this category"""
        return obj.products.count()
    product_count.short_description = 'Products'
    
    actions = ['update_all_products_tax_rate']
    
    def update_all_products_tax_rate(self, request, queryset):
        """Bulk action to update all products in selected categories"""
        updated_products = 0
        for category in queryset:
            updated_products += category.update_products_tax_rate()
        
        self.message_user(
            request,
            f'Updated tax rate for {updated_products} products across {queryset.count()} categories.'
        )
    update_all_products_tax_rate.short_description = 'Update all products tax rate in selected categories'

class ProductStockInline(admin.TabularInline):
    model = ProductStock
    extra = 1
    min_num = 5  # S, M, L, XL, XXL
    max_num = 5

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'tax_percentage', 'category_tax_match', 'hsn_code', 'available', 'created_at']
    list_filter = ['available', 'category', 'created_at', 'tax_percentage']
    search_fields = ['name', 'description', 'hsn_code']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'tax_percentage', 'hsn_code', 'available']
    inlines = [ProductStockInline, ProductImageInline]
    
    def category_tax_match(self, obj):
        """Show if product tax matches category tax"""
        if obj.category and obj.tax_percentage == obj.category.tax_percentage:
            return '✅ Matches'
        return '❌ Custom'
    category_tax_match.short_description = 'Tax Rate Status'
    category_tax_match.admin_order_field = 'tax_percentage'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Tax', {
            'fields': ('price', 'tax_percentage'),
            'description': (
                'Set the product price and GST tax rate. '
                'By default, products inherit the tax rate from their category. '
                'You can override this by setting a custom tax percentage here.'
            )
        }),
        ('Inventory & Availability', {
            'fields': ('stock', 'available'),
            'description': 'Note: Individual size stock is managed below in the Size Stock section.'
        }),
        ('Product Details', {
            'fields': ('image', 'hsn_code'),
            'description': 'HSN code is used for GST compliance and invoicing.'
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Request Details', {
            'fields': ('subject', 'message')
        }),
        ('Status & Management', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed']
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected requests as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} requests marked as in progress.')
    mark_as_in_progress.short_description = 'Mark selected requests as in progress'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected requests as resolved"""
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} requests marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected requests as resolved'
    
    def mark_as_closed(self, request, queryset):
        """Mark selected requests as closed"""
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} requests marked as closed.')
    mark_as_closed.short_description = 'Mark selected requests as closed'


@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ['admin_thumbnail', 'title', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'alt_text']
    ordering = ['order', '-created_at']
    fieldsets = (
        ('Banner Content', {
            'fields': ('image', 'title', 'subtitle', 'alt_text', 'link_url')
        }),
        ('Display', {
            'fields': ('order', 'is_active')
        }),
    )

    def admin_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;object-fit:cover;"/>', obj.image.url)
        return '—'
    admin_thumbnail.short_description = 'Preview'
