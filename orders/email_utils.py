import logging
import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.sites.models import Site
from django.db import transaction
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site

# Configure logging
logger = logging.getLogger('orders.email_utils')

class EmailService:
    """Service class for handling order and invoice emails"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'ORDER_EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
        self.site_name = getattr(settings, 'SITE_NAME', 'JOOG Wear')
        self.company_logo_url = getattr(settings, 'COMPANY_LOGO_URL', '')
        
    def send_order_confirmation_email_new(self, order, user_email: Optional[str] = None) -> Tuple[bool, str]:
        """
        Enhanced order confirmation email with better error handling
        
        Args:
            order: Order instance
            user_email: Override email address (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Determine recipient email
            recipient_email = user_email or order.user.email
            if not recipient_email:
                return False, "No email address found for customer"
            
            # Prepare context data
            context = self._prepare_order_context(order)
            context.update({
                'email_type': 'order_confirmation',
                'customer_name': self._get_customer_name(order.user),
                'site_url': self._get_site_url(),
            })
            
            # Render email templates
            html_content = render_to_string('emails/order_confirmation.html', context)
            text_content = render_to_string('emails/order_confirmation.txt', context)
            
            # Create email
            subject = f"{settings.ORDER_EMAIL_SUBJECT_PREFIX}Order Confirmation #{order.order_number}"
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[recipient_email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send()
            
            # Update order email status
            self._update_order_email_status(order, 'confirmation', True)
            
            logger.info(f"Order confirmation email sent successfully for order {order.order_number} to {recipient_email}")
            return True, "Order confirmation email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation email for order {order.order_number}: {str(e)}")
            self._update_order_email_status(order, 'confirmation', False, str(e))
            return False, f"Failed to send email: {str(e)}"
    
    def send_invoice_email(self, order, invoice=None, user_email: Optional[str] = None) -> Tuple[bool, str]:
        """
        Send tax invoice email to customer, generating the invoice (and PDF) if needed.
        
        Args:
            order: Order instance
            invoice: TaxInvoice instance (optional, will be created if not provided)
            user_email: Override email address (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            from invoices.models import TaxInvoice, TaxInvoiceItem
            from invoices.utils import generate_invoice_pdf
            
            # Get or create invoice
            if not invoice:
                invoice, created = TaxInvoice.objects.get_or_create(
                    order=order,
                    defaults={'customer_name': self._get_customer_name(order.user)}
                )
                if created:
                    invoice.populate_from_order()
            
            # Ensure invoice has items mirroring the order items
            if not invoice.items.exists():
                for order_item in order.items.all():
                    product_tax_rate = getattr(order_item.product, 'tax_percentage', 18.00)
                    TaxInvoiceItem.objects.create(
                        invoice=invoice,
                        product_name=order_item.product.name,
                        product_description=(order_item.product.description or '')[:200],
                        hsn_code=getattr(order_item.product, 'hsn_code', '') or '',
                        size=order_item.size or '',
                        quantity=order_item.quantity,
                        unit_price=order_item.price,
                        tax_percentage=product_tax_rate,
                    )
            
            # Make sure a PDF exists; generate it if missing
            if not invoice.invoice_pdf:
                pdf_ok = generate_invoice_pdf(invoice)
                if pdf_ok:
                    invoice.is_generated = True
                    invoice.save(update_fields=['is_generated'])
            
            # Determine recipient email
            recipient_email = user_email or order.user.email
            if not recipient_email:
                return False, "No email address found for customer"
            
            # Prepare context data
            context = self._prepare_order_context(order)
            context.update({
                'email_type': 'tax_invoice',
                'invoice': invoice,
                'customer_name': self._get_customer_name(order.user),
                'site_url': self._get_site_url(),
            })
            
            # Render email templates
            html_content = render_to_string('emails/tax_invoice.html', context)
            text_content = render_to_string('emails/tax_invoice.txt', context)
            
            # Create email
            subject = f"{settings.ORDER_EMAIL_SUBJECT_PREFIX}Tax Invoice #{invoice.invoice_number}"
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[recipient_email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Attach PDF invoice if available
            if invoice.invoice_pdf and os.path.exists(getattr(invoice.invoice_pdf, 'path', '')):
                with open(invoice.invoice_pdf.path, 'rb') as pdf_file:
                    msg.attach(
                        f"Invoice_{invoice.invoice_number}.pdf",
                        pdf_file.read(),
                        'application/pdf'
                    )
            
            # Send email
            msg.send()
            
            # Update order email status
            self._update_order_email_status(order, 'invoice', True)
            
            logger.info(f"Tax invoice email sent successfully for order {order.order_number} to {recipient_email}")
            return True, "Tax invoice email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send tax invoice email for order {order.order_number}: {str(e)}")
            self._update_order_email_status(order, 'invoice', False, str(e))
            return False, f"Failed to send email: {str(e)}"
    
    def _prepare_order_context(self, order) -> Dict:
        """Prepare common context data for order emails"""
        return {
            'order': order,
            'order_items': order.items.all(),
            'site_name': self.site_name,
            'company_logo_url': self.company_logo_url,
            'current_date': timezone.now(),
            'support_email': getattr(settings, 'ADMIN_EMAIL', 'support@example.com'),
            'company_address': getattr(settings, 'COMPANY_ADDRESS', ''),
            # 'company_phone': removed from customer emails per requirement
        }
    
    def _get_customer_name(self, user) -> str:
        """Get formatted customer name"""
        if user.first_name or user.last_name:
            return f"{user.first_name} {user.last_name}".strip()
        return user.username or user.email.split('@')[0]
    
    def _get_site_url(self) -> str:
        """Get site URL for email links"""
        try:
            site = Site.objects.get_current()
            protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
            return f"{protocol}://{site.domain}"
        except:
            return "https://yourdomain.com"
    
    def send_order_status_update_email(self, order, old_status, new_status) -> Tuple[bool, str]:
        """
        Send order status update email to customer

        Args:
            order: Order instance
            old_status: Previous order status
            new_status: New order status

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Skip if status hasn't actually changed
            if old_status == new_status:
                return True, "Status unchanged, no email sent"

            # Determine recipient email
            recipient_email = order.user.email
            if not recipient_email:
                return False, "No email address found for customer"

            # Prepare context data
            context = self._prepare_order_context(order)
            
            # Get display name for the status
            status_display_map = {
                'pending': 'Pending',
                'confirmed': 'Confirmed',
                'shipped': 'Shipped',
                'delivered': 'Delivered',
                'cancelled': 'Cancelled',
            }
            
            context.update({
                'email_type': 'status_update',
                'old_status': old_status,
                'new_status': new_status,
                'status_display': status_display_map.get(new_status, new_status.title()),
                'customer_name': self._get_customer_name(order.user),
                'site_url': self._get_site_url(),
            })

            # Email subject based on new status
            status_messages = {
                'confirmed': 'Order Confirmed',
                'shipped': 'Order Shipped',
                'delivered': 'Order Delivered',
                'cancelled': 'Order Cancelled',
            }

            status_message = status_messages.get(new_status, f'Order Status Updated to {new_status.title()}')
            subject = f"{getattr(settings, 'ORDER_EMAIL_SUBJECT_PREFIX', '[JOOG] ')}{status_message} - Order #{order.order_number}"

            # Render email templates
            try:
                html_content = render_to_string('emails/order_status_update.html', context)
                text_content = render_to_string('emails/order_status_update.txt', context)
            except Exception as template_error:
                # Fallback to simple text email if templates don't exist
                logger.warning(f"Email templates not found, using fallback for order {order.order_number}: {str(template_error)}")
                text_content = self._get_fallback_status_email(order, old_status, new_status)
                html_content = None

            # Create email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[recipient_email]
            )

            if html_content:
                msg.attach_alternative(html_content, "text/html")

            # Send email
            msg.send()

            logger.info(f"Order status update email sent successfully for order {order.order_number} to {recipient_email}: {old_status} -> {new_status}")
            return True, "Order status update email sent successfully"

        except Exception as e:
            logger.error(f"Failed to send order status update email for order {order.order_number}: {str(e)}")
            return False, f"Failed to send email: {str(e)}"

    def _get_fallback_status_email(self, order, old_status, new_status) -> str:
        """Generate fallback status update email content"""
        customer_name = self._get_customer_name(order.user)
        site_url = self._get_site_url()

        return f"""Hi {customer_name},

Your order #{order.order_number} status has been updated to: {new_status.title()}

You can view your order details and track its progress at: {site_url}/accounts/dashboard/

Thank you for shopping with {self.site_name}!

Best regards,
The {self.site_name} Team
"""

    def _update_order_email_status(self, order, email_type: str, success: bool, error_message: str = ""):
        """Update order email tracking status"""
        try:
            # We'll add these fields to the Order model later
            if hasattr(order, f'{email_type}_email_sent'):
                setattr(order, f'{email_type}_email_sent', success)
                setattr(order, f'{email_type}_email_sent_at', timezone.now() if success else None)
                if error_message and hasattr(order, f'{email_type}_email_error'):
                    setattr(order, f'{email_type}_email_error', error_message)
                order.save(update_fields=[
                    f'{email_type}_email_sent',
                    f'{email_type}_email_sent_at',
                    f'{email_type}_email_error'
                ])
        except Exception as e:
            logger.warning(f"Failed to update email status for order {order.order_number}: {str(e)}")

def send_order_confirmation_email(order, request=None):
    """
    Send order confirmation email to customer with tax invoice attachment
    """
    try:
        # Get the current site for URLs
        if request:
            current_site = get_current_site(request)
            site_url = f"http{'s' if request.is_secure() else ''}://{current_site.domain}"
        else:
            site_url = "http://127.0.0.1:8000"  # Fallback for development

        # Email context
        context = {
            'order': order,
            'site_url': site_url,
        }
        
        # Email subject
        subject = f"{settings.ORDER_EMAIL_SUBJECT_PREFIX}Order Confirmation - Order #{order.id}"
        
        # Email addresses
        from_email = settings.ORDER_EMAIL_FROM
        to_email = [order.user.email]
        
        # Render email templates
        text_content = render_to_string('emails/order_confirmation.txt', context)
        html_content = render_to_string('emails/order_confirmation.html', context)
        
        # Create email message
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        
        # Try to attach tax invoice if it exists and is generated
        if hasattr(order, 'tax_invoice') and order.tax_invoice.invoice_pdf:
            try:
                invoice_filename = f"Tax_Invoice_{order.tax_invoice.invoice_number}.pdf"
                msg.attach_file(order.tax_invoice.invoice_pdf.path, mimetype='application/pdf')
                logger.info(f"Tax invoice attached to order confirmation email for order #{order.id}")
            except Exception as attach_error:
                logger.warning(f"Failed to attach invoice to email for order #{order.id}: {str(attach_error)}")
        
        # Send email
        msg.send()
        
        logger.info(f"Order confirmation email sent successfully to {order.user.email} for order #{order.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order #{order.id}: {str(e)}")
        return False

def send_admin_order_notification(order, request=None):
    """
    Send order notification email to admin
    """
    try:
        # Get the current site for URLs
        if request:
            current_site = get_current_site(request)
            site_url = f"http{'s' if request.is_secure() else ''}://{current_site.domain}"
        else:
            site_url = "http://127.0.0.1:8000"  # Fallback for development

        # Email context
        context = {
            'order': order,
            'site_url': site_url,
        }
        
        # Email subject
        subject = f"{settings.ORDER_EMAIL_SUBJECT_PREFIX}New Order Received - Order #{order.id}"
        
        # Email addresses
        from_email = settings.DEFAULT_FROM_EMAIL
        admin_emails = [email for name, email in settings.ADMINS]
        
        # Render email content
        text_content = render_to_string('emails/admin_order_notification.txt', context)
        html_content = render_to_string('emails/admin_order_notification.html', context)
        
        # Create email message
        msg = EmailMultiAlternatives(subject, text_content, from_email, admin_emails)
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        msg.send()
        
        logger.info(f"Admin order notification email sent successfully for order #{order.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin order notification for order #{order.id}: {str(e)}")
        return False

def send_order_status_update_email(order, old_status, new_status, request=None):
    """
    Send order status update email to customer
    """
    try:
        # Skip if status hasn't actually changed
        if old_status == new_status:
            return True

        # Get the current site for URLs
        if request:
            current_site = get_current_site(request)
            site_url = f"http{'s' if request.is_secure() else ''}://{current_site.domain}"
        else:
            site_url = "http://127.0.0.1:8000"  # Fallback for development

        # Email context
        context = {
            'order': order,
            'old_status': old_status,
            'new_status': new_status,
            'site_url': site_url,
        }
        
        # Email subject based on new status
        status_messages = {
            'confirmed': 'Order Confirmed',
            'shipped': 'Order Shipped',
            'delivered': 'Order Delivered',
            'cancelled': 'Order Cancelled',
        }
        
        status_message = status_messages.get(new_status, f'Order Status Updated to {new_status.title()}')
        subject = f"{settings.ORDER_EMAIL_SUBJECT_PREFIX}{status_message} - Order #{order.id}"
        
        # Email addresses
        from_email = settings.ORDER_EMAIL_FROM
        to_email = [order.user.email]
        
        # Simple text email for status updates
        message = f"""
Hi {order.user.first_name or order.user.email},

Your order #{order.id} status has been updated to: {new_status.title()}

You can view your order details and track its progress at: {site_url}/accounts/dashboard/

Thank you for shopping with JOOG Wear!

Best regards,
The JOOG Wear Team
"""
        
        # Send email
        send_mail(subject, message, from_email, to_email, fail_silently=False)
        
        logger.info(f"Order status update email sent to {order.user.email} for order #{order.id} - Status: {old_status} -> {new_status}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order status update email for order #{order.id}: {str(e)}")
        return False