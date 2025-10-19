from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import TaxInvoice, TaxInvoiceItem


@receiver(post_save, sender=Order)
def create_invoice_for_order(sender, instance, created, **kwargs):
    """
    Automatically create a tax invoice when an order status changes to 'confirmed' or 'shipped'
    """
    # Only create invoice for confirmed or shipped orders
    if instance.status in ['confirmed', 'shipped'] and not hasattr(instance, 'tax_invoice'):
        try:
            # Create tax invoice
            invoice = TaxInvoice.objects.create(order=instance)
            invoice.populate_from_order()
            
            # Create invoice items from order items
            for order_item in instance.items.all():
                TaxInvoiceItem.objects.create(
                    invoice=invoice,
                    product_name=order_item.product.name,
                    product_description=order_item.product.description[:200],
                    hsn_code=getattr(order_item.product, 'hsn_code', '') or '',
                    size=order_item.size or '',
                    quantity=order_item.quantity,
                    unit_price=order_item.price,
                )
            
            # Try to generate PDF
            from .utils import generate_invoice_pdf
            pdf_generated = generate_invoice_pdf(invoice)
            
            if pdf_generated:
                invoice.is_generated = True
                invoice.save()
                
        except Exception as e:
            # Log the error but don't prevent order creation
            print(f"Error creating invoice for order {instance.order_number}: {str(e)}")
            pass