#!/usr/bin/env python
"""
Test script for the invoice system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joog_ecommerce.settings')
django.setup()

from orders.models import Order
from invoices.models import TaxInvoice, TaxInvoiceItem
from products.models import Product

def test_invoice_system():
    print("=== JOOG Invoice System Test ===\n")
    
    # Check existing orders
    orders = Order.objects.all()
    print(f"Total orders in system: {orders.count()}")
    
    if orders.exists():
        print("\nExisting orders:")
        for order in orders[:5]:
            print(f"- Order {order.order_number}: {order.status} - ₹{order.final_amount}")
            
        # Check if any orders have invoices
        invoices = TaxInvoice.objects.all()
        print(f"\nTotal invoices in system: {invoices.count()}")
        
        if invoices.exists():
            print("\nExisting invoices:")
            for invoice in invoices[:5]:
                print(f"- Invoice {invoice.invoice_number}: {invoice.order.order_number} - ₹{invoice.final_amount}")
        
        # Try to create an invoice for the first order without an invoice
        test_order = None
        for order in orders:
            if not hasattr(order, 'tax_invoice'):
                test_order = order
                break
        
        if test_order:
            print(f"\n=== Creating test invoice for order {test_order.order_number} ===")
            
            try:
                # Create tax invoice
                invoice = TaxInvoice.objects.create(order=test_order)
                invoice.populate_from_order()
                
                print(f"✓ Created invoice {invoice.invoice_number}")
                
                # Create invoice items
                for order_item in test_order.items.all():
                    TaxInvoiceItem.objects.create(
                        invoice=invoice,
                        product_name=order_item.product.name,
                        product_description=order_item.product.description[:200],
                        hsn_code=getattr(order_item.product, 'hsn_code', '') or '6109.10.00',  # Default HSN for textiles
                        size=order_item.size or '',
                        quantity=order_item.quantity,
                        unit_price=order_item.price,
                    )
                
                print(f"✓ Created {test_order.items.count()} invoice items")
                
                # Try to generate PDF
                from invoices.utils import generate_invoice_pdf
                pdf_generated = generate_invoice_pdf(invoice)
                
                if pdf_generated:
                    invoice.is_generated = True
                    invoice.save()
                    print("✓ PDF generated successfully")
                else:
                    print("⚠ PDF generation failed, but invoice created")
                
                print(f"\n=== Invoice Details ===")
                print(f"Invoice Number: {invoice.invoice_number}")
                print(f"Customer: {invoice.customer_name}")
                print(f"Subtotal: ₹{invoice.subtotal}")
                print(f"Tax (GST): ₹{invoice.total_tax}")
                print(f"Final Amount: ₹{invoice.final_amount}")
                
            except Exception as e:
                print(f"✗ Error creating invoice: {str(e)}")
                
        else:
            print("All orders already have invoices")
            
    else:
        print("No orders found in the system")
        
    # Check product HSN codes
    products = Product.objects.all()
    products_with_hsn = products.exclude(hsn_code__isnull=True).exclude(hsn_code='')
    
    print(f"\n=== Product HSN Status ===")
    print(f"Total products: {products.count()}")
    print(f"Products with HSN codes: {products_with_hsn.count()}")
    
    if products_with_hsn.exists():
        print("\nProducts with HSN codes:")
        for product in products_with_hsn[:3]:
            print(f"- {product.name}: {product.hsn_code}")
    
    print(f"\n=== Test Complete ===")
    print("You can now:")
    print("1. Visit http://127.0.0.1:8000/admin/ to manage products and orders")
    print("2. Visit http://127.0.0.1:8000/invoices/ to view invoices")
    print("3. Add HSN codes to products in the admin")
    print("4. Generate more invoices from orders")

if __name__ == "__main__":
    test_invoice_system()