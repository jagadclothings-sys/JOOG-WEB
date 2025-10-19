from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from orders.models import Order
from orders.email_utils import send_order_confirmation_email, send_admin_order_notification
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test email functionality for JOOG Wear'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email', 
            type=str, 
            help='Email address to send test emails to',
            required=True
        )
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['basic', 'order', 'all'],
            default='all',
            help='Type of email test to run'
        )
        parser.add_argument(
            '--order-id',
            type=int,
            help='Order ID to use for order email tests'
        )

    def handle(self, *args, **options):
        test_email = options['email']
        test_type = options['test_type']
        
        self.stdout.write(f"Starting email tests...")
        self.stdout.write(f"Test email: {test_email}")
        self.stdout.write(f"Email backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"SMTP host: {settings.EMAIL_HOST}")
        self.stdout.write(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        
        if test_type in ['basic', 'all']:
            self.test_basic_email(test_email)
        
        if test_type in ['order', 'all']:
            order_id = options.get('order_id')
            if order_id:
                self.test_order_email_with_id(test_email, order_id)
            else:
                self.test_order_email_mock(test_email)
        
        self.stdout.write(self.style.SUCCESS('Email tests completed!'))

    def test_basic_email(self, test_email):
        """Test basic email sending functionality"""
        self.stdout.write("\n📧 Testing basic email sending...")
        
        try:
            result = send_mail(
                subject='🧪 Test Email from JOOG Wear',
                message='This is a test email to verify your GoDaddy email integration is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Basic email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to send basic email'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Basic email test failed: {str(e)}'))

    def test_html_email(self, test_email):
        """Test HTML email functionality"""
        self.stdout.write("\n📧 Testing HTML email...")
        
        try:
            subject = '🧪 HTML Test Email from JOOG Wear'
            text_content = 'This is the plain text version of the test email.'
            html_content = '''
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #dc2626;">🧪 JOOG Wear Email Test</h2>
                <p>This is an <strong>HTML test email</strong> to verify your email configuration.</p>
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Email Configuration Status:</h3>
                    <ul>
                        <li>✅ SMTP Connection: Working</li>
                        <li>✅ HTML Rendering: Working</li>
                        <li>✅ Professional Branding: Active</li>
                    </ul>
                </div>
                <p>Best regards,<br><strong>The JOOG Wear Team</strong></p>
            </body>
            </html>
            '''
            
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [test_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            self.stdout.write(self.style.SUCCESS('✅ HTML email sent successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ HTML email test failed: {str(e)}'))

    def test_order_email_with_id(self, test_email, order_id):
        """Test order email with actual order"""
        self.stdout.write(f"\n📧 Testing order email with Order ID: {order_id}...")
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Test order confirmation email
            result = send_order_confirmation_email(order)
            if result:
                self.stdout.write(self.style.SUCCESS(f'✅ Order confirmation email sent for Order #{order_id}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Failed to send order confirmation email'))
            
            # Test admin notification email
            admin_result = send_admin_order_notification(order)
            if admin_result:
                self.stdout.write(self.style.SUCCESS(f'✅ Admin notification email sent for Order #{order_id}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Failed to send admin notification email'))
                
        except Order.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Order with ID {order_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Order email test failed: {str(e)}'))

    def test_order_email_mock(self, test_email):
        """Test order email with mock data"""
        self.stdout.write("\n📧 Testing order email templates with mock data...")
        
        try:
            # Get the most recent order for template testing
            recent_order = Order.objects.first()
            if not recent_order:
                self.stdout.write(self.style.WARNING('⚠️  No orders found. Please create a test order first.'))
                return
            
            context = {
                'order': recent_order,
                'site_url': 'http://127.0.0.1:8000',
            }
            
            # Test order confirmation template
            try:
                text_content = render_to_string('emails/order_confirmation.txt', context)
                html_content = render_to_string('emails/order_confirmation.html', context)
                
                subject = f'🧪 [JOOG] Order Email Template Test - Order #{recent_order.id}'
                
                msg = EmailMultiAlternatives(subject, text_content, settings.ORDER_EMAIL_FROM, [test_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
                self.stdout.write(self.style.SUCCESS('✅ Order confirmation template test sent!'))
                
            except Exception as template_error:
                self.stdout.write(self.style.ERROR(f'❌ Order template test failed: {str(template_error)}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Mock order email test failed: {str(e)}'))

    def test_configuration(self):
        """Test email configuration"""
        self.stdout.write("\n🔧 Email Configuration Check:")
        self.stdout.write(f"Email Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Email Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"Email Port: {settings.EMAIL_PORT}")
        self.stdout.write(f"Use TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"Use SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"Host User: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"Default From: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"Order Email From: {settings.ORDER_EMAIL_FROM}")
        
        if not settings.USE_PRODUCTION_EMAIL:
            self.stdout.write(self.style.WARNING('⚠️  Production email is disabled. Set USE_PRODUCTION_EMAIL=True in .env'))