import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Order
from .email_utils import EmailService

logger = logging.getLogger('orders.email_utils')

@receiver(post_save, sender=Order)
def handle_order_created(sender, instance, created, **kwargs):
    """
    Handle order creation - send confirmation email
    """
    if created:
        try:
            # Delay email sending slightly to ensure transaction is committed
            from django.db import transaction
            transaction.on_commit(lambda: send_order_confirmation_delayed(instance))
            logger.info(f"Scheduled confirmation email for new order {instance.order_number}")
        except Exception as e:
            logger.error(f"Failed to schedule confirmation email for order {instance.order_number}: {str(e)}")

def send_order_confirmation_delayed(order):
    """
    Send order confirmation email with delay to ensure transaction is committed
    """
    try:
        # Skip if email already sent
        if order.confirmation_email_sent:
            return
        
        # Skip if email sending is disabled in settings
        if not getattr(settings, 'SEND_ORDER_EMAILS', True):
            logger.info(f"Order emails disabled - skipping confirmation for order {order.order_number}")
            return
        
        email_service = EmailService()
        success, message = email_service.send_order_confirmation_email_new(order)
        
        if success:
            logger.info(f"Confirmation email sent successfully for order {order.order_number}")
        else:
            logger.error(f"Failed to send confirmation email for order {order.order_number}: {message}")
            
    except Exception as e:
        logger.error(f"Exception in send_order_confirmation_delayed for order {order.order_number}: {str(e)}")

@receiver(pre_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    """
    Handle order status changes - send status update emails and invoices
    """
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            old_status = old_order.status
            new_status = instance.status
            
            if old_status != new_status:
                # Schedule status update email
                from django.db import transaction
                transaction.on_commit(
                    lambda: send_status_update_delayed(instance, old_status, new_status)
                )
                logger.info(f"Scheduled status update email for order {instance.order_number}: {old_status} -> {new_status}")
                
        except Order.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            logger.warning(f"Could not find existing order {instance.pk} for status change comparison")
        except Exception as e:
            logger.error(f"Error in handle_order_status_change for order {instance.order_number}: {str(e)}")

def send_status_update_delayed(order, old_status, new_status):
    """
    Send order status update email and invoice if applicable
    """
    try:
        # Skip if email sending is disabled
        if not getattr(settings, 'SEND_ORDER_EMAILS', True):
            logger.info(f"Order emails disabled - skipping status update for order {order.order_number}")
            return
        
        email_service = EmailService()
        
        # Send status update email
        success, message = email_service.send_order_status_update_email(order, old_status, new_status)
        
        if success:
            logger.info(f"Status update email sent for order {order.order_number}: {old_status} -> {new_status}")
        else:
            logger.error(f"Failed to send status update email for order {order.order_number}: {message}")
        
        # Send invoice email for eligible status changes
        if new_status in ['confirmed', 'shipped', 'delivered'] and not order.invoice_email_sent:
            # Add small delay for invoice email
            from django.core.management import call_command
            try:
                success, message = email_service.send_invoice_email(order)
                
                if success:
                    logger.info(f"Invoice email sent for order {order.order_number}")
                else:
                    logger.error(f"Failed to send invoice email for order {order.order_number}: {message}")
                    
            except Exception as e:
                logger.error(f"Exception sending invoice email for order {order.order_number}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Exception in send_status_update_delayed for order {order.order_number}: {str(e)}")

# Signal for handling failed email retries
@receiver(post_save, sender=Order)
def handle_failed_email_retry(sender, instance, **kwargs):
    """
    Retry failed emails after some time
    """
    try:
        # Skip if disabled
        if not getattr(settings, 'RETRY_FAILED_EMAILS', True):
            return
        
        now = timezone.now()
        retry_delay = timedelta(hours=getattr(settings, 'EMAIL_RETRY_DELAY_HOURS', 2))
        
        # Retry confirmation email if failed and enough time has passed
        if (not instance.confirmation_email_sent and 
            instance.confirmation_email_error and 
            instance.created_at <= now - retry_delay):
            
            # Only retry a few times to avoid spam
            retry_count = instance.confirmation_email_error.count('retry:')
            max_retries = getattr(settings, 'MAX_EMAIL_RETRIES', 3)
            
            if retry_count < max_retries:
                from django.db import transaction
                transaction.on_commit(lambda: retry_confirmation_email(instance))
        
        # Retry invoice email if failed and enough time has passed
        if (not instance.invoice_email_sent and 
            instance.invoice_email_error and 
            instance.status in ['confirmed', 'shipped', 'delivered'] and
            instance.updated_at <= now - retry_delay):
            
            retry_count = instance.invoice_email_error.count('retry:')
            max_retries = getattr(settings, 'MAX_EMAIL_RETRIES', 3)
            
            if retry_count < max_retries:
                from django.db import transaction
                transaction.on_commit(lambda: retry_invoice_email(instance))
        
    except Exception as e:
        logger.error(f"Exception in handle_failed_email_retry for order {instance.order_number}: {str(e)}")

def retry_confirmation_email(order):
    """Retry sending confirmation email"""
    try:
        email_service = EmailService()
        success, message = email_service.send_order_confirmation_email_new(order)
        
        if success:
            logger.info(f"Retry successful - confirmation email sent for order {order.order_number}")
        else:
            # Update error message with retry count
            retry_msg = f"retry:{timezone.now().isoformat()} - {message}"
            order.confirmation_email_error += f"; {retry_msg}"
            order.save(update_fields=['confirmation_email_error'])
            logger.warning(f"Retry failed for confirmation email, order {order.order_number}: {message}")
            
    except Exception as e:
        logger.error(f"Exception in retry_confirmation_email for order {order.order_number}: {str(e)}")

def retry_invoice_email(order):
    """Retry sending invoice email"""
    try:
        email_service = EmailService()
        success, message = email_service.send_invoice_email(order)
        
        if success:
            logger.info(f"Retry successful - invoice email sent for order {order.order_number}")
        else:
            # Update error message with retry count
            retry_msg = f"retry:{timezone.now().isoformat()} - {message}"
            order.invoice_email_error += f"; {retry_msg}"
            order.save(update_fields=['invoice_email_error'])
            logger.warning(f"Retry failed for invoice email, order {order.order_number}: {message}")
            
    except Exception as e:
        logger.error(f"Exception in retry_invoice_email for order {order.order_number}: {str(e)}")

# Optional: Signal for cleaning up old error messages
@receiver(post_save, sender=Order)
def cleanup_old_email_errors(sender, instance, **kwargs):
    """
    Clean up old email error messages to prevent database bloat
    """
    try:
        cleanup_enabled = getattr(settings, 'CLEANUP_EMAIL_ERRORS', True)
        max_error_age_days = getattr(settings, 'EMAIL_ERROR_RETENTION_DAYS', 30)
        
        if not cleanup_enabled:
            return
        
        cutoff_date = timezone.now() - timedelta(days=max_error_age_days)
        
        # Clear old error messages
        if (instance.confirmation_email_error and 
            instance.confirmation_email_sent and 
            instance.confirmation_email_sent_at and
            instance.confirmation_email_sent_at < cutoff_date):
            
            instance.confirmation_email_error = ""
            instance.save(update_fields=['confirmation_email_error'])
        
        if (instance.invoice_email_error and 
            instance.invoice_email_sent and 
            instance.invoice_email_sent_at and
            instance.invoice_email_sent_at < cutoff_date):
            
            instance.invoice_email_error = ""
            instance.save(update_fields=['invoice_email_error'])
            
    except Exception as e:
        logger.error(f"Exception in cleanup_old_email_errors for order {instance.order_number}: {str(e)}")