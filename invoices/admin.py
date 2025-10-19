from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Sum
from .models import TaxInvoice, TaxInvoiceItem
from .views import export_invoices_excel, export_sales_report_excel
import datetime

class TaxInvoiceItemInline(admin.TabularInline):
    model = TaxInvoiceItem
    extra = 0
    readonly_fields = ['tax_amount', 'total_price']
    fields = ['product_name', 'hsn_code', 'size', 'quantity', 'unit_price', 'tax_percentage', 'tax_amount', 'total_price']
    
    def get_readonly_fields(self, request, obj=None):
        # Make calculated fields readonly
        return ['tax_amount', 'total_price']

@admin.register(TaxInvoice)
class TaxInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'customer_name', 'final_amount', 'is_generated', 'print_invoice', 'created_at']
    list_filter = ['is_generated', 'created_at', 'invoice_date', 'shipping_state']
    search_fields = ['invoice_number', 'customer_name', 'customer_email', 'order__order_number']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at', 'total_tax']
    inlines = [TaxInvoiceItemInline]
    actions = ['export_selected_invoices', 'generate_pdf_invoices', 'mark_as_generated']
    list_per_page = 25
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'order', 'invoice_date', 'due_date', 'is_generated')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_gstin', 'company_address', 'company_phone', 'company_email', 'company_website')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Tax Configuration', {
            'fields': ('cgst_rate', 'sgst_rate', 'igst_rate')
        }),
        ('Amount Details', {
            'fields': ('subtotal', 'cgst_amount', 'sgst_amount', 'igst_amount', 'total_tax', 'discount_amount', 'final_amount')
        }),
        ('Invoice File', {
            'fields': ('invoice_pdf',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def print_invoice(self, obj):
        """Add print button to list view"""
        from django.utils.html import format_html
        print_url = f'/invoices/admin/detail/{obj.id}/?print=true'
        return format_html(
            '<a href="{}" target="_blank" class="button">🖨️ Print</a>',
            print_url
        )
    print_invoice.short_description = 'Actions'
    
    def export_selected_invoices(self, request, queryset):
        """Export selected invoices to Excel"""
        # Create a temporary request with invoice IDs
        invoice_ids = list(queryset.values_list('id', flat=True))
        request.session['selected_invoice_ids'] = invoice_ids
        return redirect('/invoices/admin/export/selected-invoices/')
    export_selected_invoices.short_description = "📊 Export selected invoices to Excel"
    
    def generate_pdf_invoices(self, request, queryset):
        """Generate PDF for selected invoices"""
        from .utils import generate_invoice_pdf
        generated_count = 0
        for invoice in queryset:
            if generate_invoice_pdf(invoice):
                invoice.is_generated = True
                invoice.save()
                generated_count += 1
        
        messages.success(request, f'Generated {generated_count} PDF invoices successfully.')
    generate_pdf_invoices.short_description = "📄 Generate PDF for selected invoices"
    
    def mark_as_generated(self, request, queryset):
        """Mark selected invoices as generated"""
        updated = queryset.update(is_generated=True)
        messages.success(request, f'{updated} invoices marked as generated.')
    mark_as_generated.short_description = "✅ Mark selected as generated"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/selected-invoices/', self.admin_site.admin_view(self.export_selected_invoices_view), name='export_selected_invoices'),
            path('export/all-invoices/', self.admin_site.admin_view(export_invoices_excel), name='export_all_invoices'),
            path('export/sales-report/', self.admin_site.admin_view(export_sales_report_excel), name='export_sales_report'),
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='invoice_analytics'),
        ]
        return custom_urls + urls
    
    def export_selected_invoices_view(self, request):
        """Export selected invoices from session"""
        invoice_ids = request.session.get('selected_invoice_ids', [])
        if not invoice_ids:
            messages.error(request, 'No invoices selected for export.')
            return redirect('admin:invoices_taxinvoice_changelist')
        
        # Filter invoices by selected IDs
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        # Construct export URL with invoice IDs
        export_url = reverse('invoices:export_excel')
        invoice_ids_param = ','.join(map(str, invoice_ids))
        return HttpResponseRedirect(f'{export_url}?invoice_ids={invoice_ids_param}')
    
    def analytics_view(self, request):
        """Show invoice analytics directly in admin"""
        from django.template.response import TemplateResponse
        from django.db.models import Count, Sum, Avg
        from datetime import datetime, timedelta
        
        # Calculate analytics
        total_invoices = TaxInvoice.objects.count()
        generated_invoices = TaxInvoice.objects.filter(is_generated=True).count()
        total_revenue = TaxInvoice.objects.aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        avg_invoice_value = TaxInvoice.objects.aggregate(Avg('final_amount'))['final_amount__avg'] or 0
        
        # This month's data
        current_month = datetime.now().replace(day=1)
        monthly_invoices = TaxInvoice.objects.filter(created_at__gte=current_month).count()
        monthly_revenue = TaxInvoice.objects.filter(
            created_at__gte=current_month
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        # Recent invoices
        recent_invoices = TaxInvoice.objects.select_related('order').order_by('-created_at')[:10]
        
        # Status breakdown
        from orders.models import Order
        orders_without_invoices = Order.objects.filter(
            status__in=['confirmed', 'shipped']
        ).exclude(tax_invoice__isnull=False)[:10]
        
        context = {
            'title': 'Invoice Analytics Dashboard',
            'total_invoices': total_invoices,
            'generated_invoices': generated_invoices,
            'pending_invoices': total_invoices - generated_invoices,
            'total_revenue': total_revenue,
            'avg_invoice_value': avg_invoice_value,
            'monthly_invoices': monthly_invoices,
            'monthly_revenue': monthly_revenue,
            'recent_invoices': recent_invoices,
            'orders_without_invoices': orders_without_invoices,
            'opts': self.model._meta,
            'has_permission': True,
        }
        
        return TemplateResponse(request, 'admin/invoices/analytics.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """Add custom context to changelist"""
        extra_context = extra_context or {}
        
        # Add quick stats
        extra_context['total_invoices'] = TaxInvoice.objects.count()
        extra_context['generated_count'] = TaxInvoice.objects.filter(is_generated=True).count()
        extra_context['total_revenue'] = TaxInvoice.objects.aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        return super().changelist_view(request, extra_context)

@admin.register(TaxInvoiceItem)
class TaxInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'product_name', 'hsn_code', 'size', 'quantity', 'unit_price', 'tax_percentage', 'tax_amount', 'total_price']
    list_filter = ['invoice__created_at', 'size', 'tax_percentage']
    search_fields = ['product_name', 'hsn_code', 'invoice__invoice_number']
    list_editable = ['quantity', 'unit_price', 'tax_percentage']  # Allow editing amounts and tax directly in list view
    readonly_fields = ['tax_amount', 'total_price']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('invoice', 'product_name', 'product_description', 'hsn_code', 'size')
        }),
        ('Pricing & Tax', {
            'fields': ('quantity', 'unit_price', 'tax_percentage', 'tax_amount', 'total_price'),
            'description': 'Edit quantity, unit price and tax percentage. Tax amount and total price are calculated automatically.'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Tax calculation is handled in the model's save method
        super().save_model(request, obj, form, change)
        
        # Also recalculate the invoice totals
        if obj.invoice:
            obj.invoice.calculate_taxes()
            obj.invoice.save()
