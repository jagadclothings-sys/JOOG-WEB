from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.conf import settings
from io import BytesIO
import os

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    # Handle both import errors and Windows dependency issues
    WEASYPRINT_AVAILABLE = False
    print(f"WeasyPrint not available: {e}")

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    XHTML2PDF_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_invoice_pdf(invoice):
    """
    Generate PDF for tax invoice using WeasyPrint (preferred), ReportLab, or xhtml2pdf as fallback
    Ensures line items exist on the invoice (copied from the order) before rendering.
    """
    if not WEASYPRINT_AVAILABLE and not REPORTLAB_AVAILABLE and not XHTML2PDF_AVAILABLE:
        print("Warning: No PDF generation library available. Install WeasyPrint, ReportLab, or xhtml2pdf.")
        return False
    
    try:
        # Ensure invoice has line items; if missing, create from order items now
        try:
            from .models import TaxInvoiceItem
        except Exception:
            TaxInvoiceItem = None
        
        if TaxInvoiceItem and not invoice.items.exists() and hasattr(invoice, 'order'):
            for order_item in invoice.order.items.all():
                product_tax_rate = getattr(order_item.product, 'tax_percentage', 5.00)
                # Note: order_item.price is tax-inclusive, TaxInvoiceItem will separate tax in save()
                TaxInvoiceItem.objects.create(
                    invoice=invoice,
                    product_name=order_item.product.name,
                    product_description=(order_item.product.description or '')[:200],
                    hsn_code=getattr(order_item.product, 'hsn_code', '') or '',
                    size=order_item.size or '',
                    quantity=order_item.quantity,
                    unit_price=order_item.price,  # Tax-inclusive price from order
                    tax_percentage=product_tax_rate,
                )
        
        # Render HTML template
        template = get_template('invoices/invoice_pdf.html')
        context = {
            'invoice': invoice,
            'invoice_items': invoice.items.all(),
        }
        html_string = template.render(context)
        
        if WEASYPRINT_AVAILABLE:
            return _generate_with_weasyprint(invoice, html_string)
        elif REPORTLAB_AVAILABLE:
            return _generate_with_reportlab(invoice)
        elif XHTML2PDF_AVAILABLE:
            return _generate_with_xhtml2pdf(invoice, html_string)
        
        return False
        
    except Exception as e:
        print(f"Error generating PDF for invoice {invoice.invoice_number}: {str(e)}")
        return False


def _generate_with_weasyprint(invoice, html_string):
    """Generate PDF using WeasyPrint (better quality)"""
    try:
        font_config = FontConfiguration()
        
        # Define CSS for the PDF
        css_string = '''
        @page {
            size: A4;
            margin: 0.5in;
        }
        body {
            font-family: 'Arial', sans-serif;
            font-size: 12px;
            line-height: 1.4;
        }
        .header { margin-bottom: 20px; }
        .invoice-details { margin-bottom: 15px; }
        .company-details { margin-bottom: 15px; }
        .customer-details { margin-bottom: 20px; }
        .invoice-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .invoice-table th, .invoice-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .invoice-table th { background-color: #f5f5f5; font-weight: bold; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .total-section { margin-top: 20px; }
        .footer { margin-top: 30px; font-size: 10px; color: #666; }
        '''
        
        html_doc = HTML(string=html_string, base_url=settings.BASE_DIR)
        css_doc = CSS(string=css_string, font_config=font_config)
        
        pdf_buffer = BytesIO()
        html_doc.write_pdf(pdf_buffer, stylesheets=[css_doc], font_config=font_config)
        pdf_buffer.seek(0)
        
        # Save PDF file
        filename = f"{invoice.invoice_number}.pdf"
        invoice.invoice_pdf.save(
            filename,
            ContentFile(pdf_buffer.getvalue()),
            save=True
        )
        
        return True
        
    except Exception as e:
        print(f"WeasyPrint error: {str(e)}")
        return False


def _generate_with_reportlab(invoice):
    """Generate PDF using ReportLab (good alternative)"""
    try:
        from django.utils import timezone
        
        pdf_buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
            title=f"Tax Invoice - {invoice.invoice_number}"
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            spaceAfter=20,
            textColor=colors.HexColor('#dc2626'),
            alignment=TA_CENTER
        )
        
        company_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=10,
            textColor=colors.HexColor('#1f2937'),
            alignment=TA_CENTER
        )
        
        # Build content
        story = []
        
        # Company header
        story.append(Paragraph(invoice.company_name, company_style))
        story.append(Spacer(1, 10))
        
        # Invoice title
        story.append(Paragraph("TAX INVOICE", title_style))
        story.append(Spacer(1, 20))
        
        # Invoice details
        invoice_data = [
            ['Invoice Number:', invoice.invoice_number, 'Invoice Date:', invoice.invoice_date.strftime('%d/%m/%Y')],
            ['Order Number:', invoice.order.order_number, 'Order Date:', invoice.order.created_at.strftime('%d/%m/%Y')],
            ['GSTIN:', invoice.company_gstin or 'N/A', 'Place of Supply:', f"{invoice.shipping_state}, {invoice.shipping_country}"]
        ]
        
        details_table = Table(invoice_data, colWidths=[80, 120, 80, 120])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8f9fa')),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Address table
        bill_to = f"<b>{invoice.customer_name}</b><br/>{invoice.customer_email}<br/>{invoice.customer_phone or ''}"
        ship_to = f"{invoice.shipping_address}<br/>{invoice.shipping_city}, {invoice.shipping_state}<br/>{invoice.shipping_postal_code}<br/>{invoice.shipping_country}"
        
        address_data = [
            ['BILL TO:', 'SHIP TO:'],
            [Paragraph(bill_to, styles['Normal']), Paragraph(ship_to, styles['Normal'])]
        ]
        
        address_table = Table(address_data, colWidths=[200, 200])
        address_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        
        story.append(address_table)
        story.append(Spacer(1, 20))
        
        # Items table
        headers = ['S.No', 'Product', 'HSN', 'Qty', 'Rate', 'Tax %', 'Amount']
        items_data = [headers]
        
        for idx, item in enumerate(invoice.items.all(), 1):
            # Show tax-exclusive unit price in the Rate column for GST compliance
            tax_exclusive_unit_price = item.unit_price_without_tax
            row = [
                str(idx),
                f"{item.product_name}\n{f'Size: {item.size}' if item.size else ''}",
                item.hsn_code or 'N/A',
                str(item.quantity),
                f"₹{tax_exclusive_unit_price:.2f}",  # Tax-exclusive rate
                f"{item.tax_percentage:.1f}%",
                f"₹{item.total_price:.2f}"  # Tax-inclusive total
            ]
            items_data.append(row)
        
        items_table = Table(items_data, colWidths=[30, 120, 50, 30, 60, 45, 65])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Tax calculation
        tax_data = []
        tax_data.append(['Taxable Amount:', f"₹{invoice.subtotal:.2f}"])
        
        if invoice.cgst_amount > 0:
            tax_data.append([f'CGST @ {invoice.cgst_rate}%:', f"₹{invoice.cgst_amount:.2f}"])
            tax_data.append([f'SGST @ {invoice.sgst_rate}%:', f"₹{invoice.sgst_amount:.2f}"])
        
        if invoice.igst_amount > 0:
            tax_data.append([f'IGST @ {invoice.igst_rate}%:', f"₹{invoice.igst_amount:.2f}"])
        
        tax_data.append(['Total Tax:', f"₹{invoice.total_tax:.2f}"])
        
        if invoice.discount_amount > 0:
            tax_data.append(['Discount:', f"-₹{invoice.discount_amount:.2f}"])
        
        tax_data.append([Paragraph('<b>Grand Total:</b>', styles['Normal']), Paragraph(f"<b>₹{invoice.final_amount:.2f}</b>", styles['Normal'])])
        
        tax_table = Table(tax_data, colWidths=[300, 100], hAlign='RIGHT')
        tax_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ]))
        
        story.append(tax_table)
        story.append(Spacer(1, 20))
        
        # Terms
        story.append(Paragraph("<b>Terms & Conditions:</b>", styles['Normal']))
        story.append(Paragraph("1. This is a computer-generated invoice and is valid without signature.", styles['Normal']))
        story.append(Paragraph("2. Please retain this invoice for warranty claims and tax purposes.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(
            f"<b>Thank you for your business!</b><br/>"
            f"Generated on: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>"
            f"This invoice was generated electronically.",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        
        # Save PDF file
        filename = f"{invoice.invoice_number}.pdf"
        invoice.invoice_pdf.save(
            filename,
            ContentFile(pdf_buffer.getvalue()),
            save=True
        )
        
        return True
        
    except Exception as e:
        print(f"ReportLab error: {str(e)}")
        return False


def _generate_with_xhtml2pdf(invoice, html_string):
    """Generate PDF using xhtml2pdf (fallback)"""
    try:
        pdf_buffer = BytesIO()
        
        # Generate PDF
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_buffer)
        
        if pisa_status.err:
            print(f"xhtml2pdf error: {pisa_status.err}")
            return False
        
        pdf_buffer.seek(0)
        
        # Save PDF file
        filename = f"{invoice.invoice_number}.pdf"
        invoice.invoice_pdf.save(
            filename,
            ContentFile(pdf_buffer.getvalue()),
            save=True
        )
        
        return True
        
    except Exception as e:
        print(f"xhtml2pdf error: {str(e)}")
        return False


def send_invoice_email(invoice, recipient_email=None):
    """Send invoice via email"""
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string
    
    if not recipient_email:
        recipient_email = invoice.customer_email
    
    if not invoice.invoice_pdf:
        if not generate_invoice_pdf(invoice):
            return False
    
    try:
        # Render email template
        subject = f'Tax Invoice {invoice.invoice_number} - {invoice.company_name}'
        
        email_body = render_to_string('invoices/invoice_email.html', {
            'invoice': invoice,
            'customer_name': invoice.customer_name,
        })
        
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        
        # Attach PDF
        if invoice.invoice_pdf:
            email.attach_file(invoice.invoice_pdf.path)
        
        email.content_subtype = 'html'  # Set email to HTML format
        email.send()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False