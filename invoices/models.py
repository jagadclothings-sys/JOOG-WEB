from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from orders.models import Order
from decimal import Decimal
from datetime import datetime

User = get_user_model()

class TaxInvoice(models.Model):
    # Invoice identification
    invoice_number = models.CharField(max_length=50, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tax_invoice')
    
    # Invoice dates
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Company details
    company_name = models.CharField(max_length=200, default='JOOG')
    company_gstin = models.CharField(max_length=15, default='')
    company_address = models.TextField(default='Your Company Address\nCity, State - Postal Code')
    company_phone = models.CharField(max_length=20, blank=True)
    company_email = models.EmailField(blank=True)
    company_website = models.URLField(blank=True)
    
    # Customer billing details (copied from order for record keeping)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Shipping address (copied from order)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Invoice amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # GST configuration
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.50'))  # 2.5%
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.50'))  # 2.5%
    igst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))  # 5%
    
    # Invoice file
    invoice_pdf = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Status and tracking
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        super().save(*args, **kwargs)
    
    def _generate_invoice_number(self):
        from django.utils import timezone
        from django.db.models import Max
        import re
        
        today = timezone.now()
        year = today.year
        month = today.month
        
        # Pattern: INV-YYYY-MM-XXXX
        pattern = f"INV-{year:04d}-{month:02d}-"
        
        # Get the highest invoice number for this month
        month_invoices = TaxInvoice.objects.filter(
            invoice_number__startswith=pattern
        ).aggregate(max_num=Max('invoice_number'))
        
        if month_invoices['max_num']:
            # Extract the counter from the last invoice number
            last_invoice = month_invoices['max_num']
            match = re.search(r'INV-\d{4}-\d{2}-(\d{4})', last_invoice)
            if match:
                counter = int(match.group(1)) + 1
            else:
                counter = 1
        else:
            counter = 1
        
        return f"INV-{year:04d}-{month:02d}-{counter:04d}"
    
    def calculate_taxes(self):
        """Calculate GST based on shipping state"""
        # Assuming company is in Karnataka (state code 29)
        company_state_code = '29'
        customer_state_code = '29'  # You can extract this from postal code or set manually
        
        # Reset tax amounts
        self.cgst_amount = Decimal('0.00')
        self.sgst_amount = Decimal('0.00')
        self.igst_amount = Decimal('0.00')
        
        if company_state_code == customer_state_code:
            # Same state - apply CGST + SGST
            self.cgst_amount = (self.subtotal * self.cgst_rate) / Decimal('100')
            self.sgst_amount = (self.subtotal * self.sgst_rate) / Decimal('100')
        else:
            # Different state - apply IGST
            self.igst_amount = (self.subtotal * self.igst_rate) / Decimal('100')
        
        self.total_tax = self.cgst_amount + self.sgst_amount + self.igst_amount
        self.final_amount = self.subtotal + self.total_tax - self.discount_amount
        
        return {
            'cgst': self.cgst_amount,
            'sgst': self.sgst_amount,
            'igst': self.igst_amount,
            'total_tax': self.total_tax,
            'final_amount': self.final_amount
        }
    
    def populate_company_details(self):
        """Populate company details from Django settings"""
        self.company_name = getattr(settings, 'COMPANY_NAME', 'JOOG')
        self.company_gstin = getattr(settings, 'COMPANY_GSTIN', '')
        self.company_address = getattr(settings, 'COMPANY_ADDRESS', '')
        self.company_phone = getattr(settings, 'COMPANY_PHONE', '')
        self.company_email = getattr(settings, 'COMPANY_EMAIL', '')
        self.company_website = getattr(settings, 'COMPANY_WEBSITE', '')
        
    def populate_from_order(self):
        """Populate invoice data from the associated order"""
        if not self.order:
            return
        
        # Populate company details from settings
        self.populate_company_details()
        
        # Customer details
        self.customer_name = f"{self.order.user.first_name} {self.order.user.last_name}".strip() or self.order.user.username
        self.customer_email = self.order.user.email
        
        # Shipping details
        self.shipping_address = self.order.shipping_address
        self.shipping_city = self.order.shipping_city
        self.shipping_state = self.order.shipping_state
        self.shipping_postal_code = self.order.shipping_postal_code
        self.shipping_country = self.order.shipping_country
        
        # Amount details - FIXED: Calculate tax-exclusive subtotal from tax-inclusive order total
        # Order total_amount includes tax (5% = 2.5% CGST + 2.5% SGST)
        # To get tax-exclusive amount: subtotal = total_amount / (1 + tax_rate/100)
        tax_rate = Decimal('5.00')  # Total GST rate (CGST + SGST)
        tax_multiplier = (Decimal('100') + tax_rate) / Decimal('100')  # 1.05
        
        # Calculate tax-exclusive subtotal
        self.subtotal = self.order.total_amount / tax_multiplier
        self.discount_amount = self.order.discount_amount
        
        # Calculate taxes on the tax-exclusive subtotal
        self.calculate_taxes()
        
        self.save()

class TaxInvoiceItem(models.Model):
    """Individual items in the tax invoice"""
    invoice = models.ForeignKey(TaxInvoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(blank=True)
    hsn_code = models.CharField(max_length=10, blank=True)
    size = models.CharField(max_length=10, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text="Tax rate for this item")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Calculated tax amount")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name} ({self.size})"
    
    @property
    def base_amount(self):
        """Calculate tax-exclusive base amount (quantity × tax-exclusive unit_price)"""
        tax_multiplier = (Decimal('100') + self.tax_percentage) / Decimal('100')
        tax_exclusive_unit_price = self.unit_price / tax_multiplier
        return self.quantity * tax_exclusive_unit_price
    
    @property
    def unit_price_with_tax(self):
        """Return unit price with tax (this is the stored unit_price as it's already tax-inclusive)"""
        return self.unit_price
    
    @property
    def unit_price_without_tax(self):
        """Calculate tax-exclusive unit price"""
        tax_multiplier = (Decimal('100') + self.tax_percentage) / Decimal('100')
        return self.unit_price / tax_multiplier
    
    def save(self, *args, **kwargs):
        # FIXED: Handle tax-inclusive pricing correctly
        # unit_price comes from order and is tax-inclusive
        # We need to separate it into tax-exclusive base + tax amount
        
        # Calculate tax-exclusive unit price
        tax_multiplier = (Decimal('100') + self.tax_percentage) / Decimal('100')
        tax_exclusive_unit_price = self.unit_price / tax_multiplier
        
        # Calculate base amount (tax-exclusive)
        base_amount = Decimal(str(self.quantity)) * tax_exclusive_unit_price
        
        # Calculate tax amount
        self.tax_amount = (base_amount * self.tax_percentage) / Decimal('100')
        
        # Total price should equal original unit_price * quantity (tax-inclusive)
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        
        super().save(*args, **kwargs)
