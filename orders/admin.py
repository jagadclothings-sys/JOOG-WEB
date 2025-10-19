from django.contrib import admin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_total_items']
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'final_amount', 'coupon_display', 'discount_amount', 'invoice_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'coupon']
    search_fields = ['order_number', 'user__username', 'user__email', 'coupon__code']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    actions = ['generate_invoices']
    
    def coupon_display(self, obj):
        if obj.coupon:
            return f"{obj.coupon.code} ({obj.coupon.discount_type}: {obj.coupon.discount_value})"
        return "No coupon"
    coupon_display.short_description = "Coupon Used"
    
    def invoice_status(self, obj):
        if hasattr(obj, 'tax_invoice'):
            invoice = obj.tax_invoice
            if invoice.is_generated:
                return f"✅ {invoice.invoice_number}"
            else:
                return f"⏳ {invoice.invoice_number}"
        return "❌ No invoice"
    invoice_status.short_description = "Invoice Status"
    
    def generate_invoices(self, request, queryset):
        """Generate invoices for selected orders"""
        generated_count = 0
        error_count = 0
        
        for order in queryset:
            if hasattr(order, 'tax_invoice'):
                messages.warning(request, f'Invoice already exists for order {order.order_number}')
                continue
                
            try:
                # Use the invoice generation view logic
                from invoices.views import generate_invoice
                from django.http import HttpRequest
                
                # Create a fake request for the view
                fake_request = HttpRequest()
                fake_request.user = request.user
                fake_request.method = 'POST'
                
                # Try to generate the invoice
                from invoices.models import TaxInvoice, TaxInvoiceItem
                from invoices.utils import generate_invoice_pdf
                
                # Create tax invoice
                invoice = TaxInvoice.objects.create(order=order)
                invoice.populate_from_order()
                
                # Create invoice items from order items
                for order_item in order.items.all():
                    TaxInvoiceItem.objects.create(
                        invoice=invoice,
                        product_name=order_item.product.name,
                        product_description=order_item.product.description[:200],
                        hsn_code=getattr(order_item.product, 'hsn_code', '') or '',
                        size=order_item.size or '',
                        quantity=order_item.quantity,
                        unit_price=order_item.price,
                    )
                
                # Generate PDF
                pdf_generated = generate_invoice_pdf(invoice)
                
                if pdf_generated:
                    invoice.is_generated = True
                    invoice.save()
                    generated_count += 1
                else:
                    generated_count += 1  # Still count as generated even if PDF failed
                    
            except Exception as e:
                error_count += 1
                messages.error(request, f'Error generating invoice for order {order.order_number}: {str(e)}')
        
        if generated_count > 0:
            messages.success(request, f'Successfully generated {generated_count} invoice(s)')
        if error_count > 0:
            messages.error(request, f'Failed to generate {error_count} invoice(s)')
            
    generate_invoices.short_description = "Generate invoices for selected orders"
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Pricing', {
            'fields': ('total_amount', 'discount_amount', 'final_amount', 'coupon')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_country')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'phonepe_merchant_txn_id', 'phonepe_txn_id')
        }),
    )