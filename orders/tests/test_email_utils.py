import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from orders.models import Order, OrderItem
from orders.email_utils import EmailService
from invoices.models import TaxInvoice
from products.models import Product, Category

User = get_user_model()

class EmailServiceTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create test category and product
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('100.00'),
            description='Test product description'
        )
        
        # Create test order
        self.order = Order.objects.create(
            user=self.user,
            order_number='TEST-001',
            status='pending',
            total_amount=Decimal('100.00'),
            final_amount=Decimal('100.00'),
            shipping_address='123 Test Street',
            shipping_city='Test City',
            shipping_state='Test State',
            shipping_postal_code='12345',
            shipping_country='Test Country',
            payment_method='phonepe',
            payment_status='completed'
        )
        
        # Create order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('100.00'),
            size='M'
        )
        
        self.email_service = EmailService()
    
    def test_send_order_confirmation_email_success(self):
        """Test successful order confirmation email sending"""
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            success, message = self.email_service.send_order_confirmation_email_new(self.order)
            
            self.assertTrue(success)
            self.assertEqual(message, "Order confirmation email sent successfully")
            
            # Check that email was sent
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            
            self.assertIn('Order Confirmation', email.subject)
            self.assertIn(self.order.order_number, email.subject)
            self.assertEqual(email.to, [self.user.email])
            
            # Check that order was updated
            self.order.refresh_from_db()
            self.assertTrue(self.order.confirmation_email_sent)
            self.assertIsNotNone(self.order.confirmation_email_sent_at)
    
    def test_send_order_confirmation_email_no_email_address(self):
        """Test order confirmation email with no user email"""
        self.user.email = ''
        self.user.save()
        
        success, message = self.email_service.send_order_confirmation_email_new(self.order)
        
        self.assertFalse(success)
        self.assertEqual(message, "No email address found for customer")
    
    def test_send_order_confirmation_email_override_email(self):
        """Test order confirmation email with override email address"""
        override_email = 'override@example.com'
        
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            success, message = self.email_service.send_order_confirmation_email_new(
                self.order, user_email=override_email
            )
            
            self.assertTrue(success)
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.to, [override_email])
    
    @patch('orders.email_utils.EmailMultiAlternatives.send')
    def test_send_order_confirmation_email_failure(self, mock_send):
        """Test order confirmation email sending failure"""
        mock_send.side_effect = Exception("SMTP error")
        
        success, message = self.email_service.send_order_confirmation_email_new(self.order)
        
        self.assertFalse(success)
        self.assertIn("Failed to send email", message)
        
        # Check that order was updated with error
        self.order.refresh_from_db()
        self.assertFalse(self.order.confirmation_email_sent)
        self.assertIn("SMTP error", self.order.confirmation_email_error)
    
    def test_send_invoice_email_success(self):
        """Test successful invoice email sending"""
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            # Mock PDF generation since we don't want to actually generate files in tests
            with patch('invoices.utils.generate_invoice_pdf') as mock_pdf_gen:
                mock_pdf_gen.return_value = '/fake/path/to/invoice.pdf'
                
                success, message = self.email_service.send_invoice_email(self.order)
                
                self.assertTrue(success)
                self.assertEqual(message, "Tax invoice email sent successfully")
                
                # Check that email was sent
                self.assertEqual(len(mail.outbox), 1)
                email = mail.outbox[0]
                
                self.assertIn('Tax Invoice', email.subject)
                self.assertEqual(email.to, [self.user.email])
                
                # Check that order was updated
                self.order.refresh_from_db()
                self.assertTrue(self.order.invoice_email_sent)
                self.assertIsNotNone(self.order.invoice_email_sent_at)
                
                # Check that invoice was created
                self.assertTrue(hasattr(self.order, 'tax_invoice'))
    
    def test_send_invoice_email_no_email_address(self):
        """Test invoice email with no user email"""
        self.user.email = ''
        self.user.save()
        
        success, message = self.email_service.send_invoice_email(self.order)
        
        self.assertFalse(success)
        self.assertEqual(message, "No email address found for customer")
    
    def test_send_order_status_update_email(self):
        """Test order status update email"""
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            success, message = self.email_service.send_order_status_update_email(
                self.order, 'pending', 'confirmed'
            )
            
            self.assertTrue(success)
            self.assertEqual(message, "Order status update email sent successfully")
            
            # Check that email was sent
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            
            self.assertIn('Order Confirmed', email.subject)
            self.assertEqual(email.to, [self.user.email])
    
    def test_send_order_status_update_email_non_eligible_status(self):
        """Test order status update email for non-eligible status"""
        success, message = self.email_service.send_order_status_update_email(
            self.order, 'pending', 'processing'
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Status update email not required for this status")
    
    def test_get_customer_name(self):
        """Test customer name formatting"""
        # Test with first and last name
        name = self.email_service._get_customer_name(self.user)
        self.assertEqual(name, "Test User")
        
        # Test with no names
        user_no_names = User.objects.create_user(
            username='nonames',
            email='nonames@example.com'
        )
        name = self.email_service._get_customer_name(user_no_names)
        self.assertEqual(name, "nonames")
        
        # Test with only first name
        user_firstname_only = User.objects.create_user(
            username='firstonly',
            email='first@example.com',
            first_name='FirstOnly'
        )
        name = self.email_service._get_customer_name(user_firstname_only)
        self.assertEqual(name, "FirstOnly")
    
    def test_prepare_order_context(self):
        """Test order context preparation"""
        context = self.email_service._prepare_order_context(self.order)
        
        self.assertIn('order', context)
        self.assertIn('order_items', context)
        self.assertIn('site_name', context)
        self.assertIn('current_date', context)
        self.assertIn('support_email', context)
        
        self.assertEqual(context['order'], self.order)
        self.assertEqual(list(context['order_items']), [self.order_item])

class EmailCommandTestCase(TestCase):
    def setUp(self):
        """Set up test data for command tests"""
        self.user = User.objects.create_user(
            username='cmduser',
            email='cmd@example.com',
            first_name='Command',
            last_name='User'
        )
        
        self.category = Category.objects.create(name='Command Category')
        self.product = Product.objects.create(
            name='Command Product',
            category=self.category,
            price=Decimal('50.00')
        )
        
        # Create orders with different email statuses
        self.order_needs_confirmation = Order.objects.create(
            user=self.user,
            order_number='CMD-001',
            total_amount=Decimal('50.00'),
            final_amount=Decimal('50.00'),
            shipping_address='456 Command St',
            shipping_city='Command City',
            shipping_state='Command State',
            shipping_postal_code='54321',
            shipping_country='Command Country',
            confirmation_email_sent=False
        )
        
        self.order_confirmation_sent = Order.objects.create(
            user=self.user,
            order_number='CMD-002',
            total_amount=Decimal('75.00'),
            final_amount=Decimal('75.00'),
            shipping_address='789 Sent St',
            shipping_city='Sent City',
            shipping_state='Sent State',
            shipping_postal_code='98765',
            shipping_country='Sent Country',
            confirmation_email_sent=True,
            confirmation_email_sent_at=timezone.now()
        )
    
    @patch('orders.email_utils.EmailService.send_order_confirmation_email_new')
    def test_send_order_confirmations_command(self, mock_send_email):
        """Test the send_order_confirmations management command"""
        from django.core.management import call_command
        from io import StringIO
        
        mock_send_email.return_value = (True, "Email sent successfully")
        
        out = StringIO()
        call_command('send_order_confirmations', '--dry-run', stdout=out)
        
        output = out.getvalue()
        
        # Should show the order that needs confirmation
        self.assertIn('CMD-001', output)
        self.assertIn('DRY RUN', output)
        
        # Mock should not have been called in dry run
        mock_send_email.assert_not_called()
    
    @patch('orders.email_utils.EmailService.send_invoice_email')
    def test_send_invoices_command(self, mock_send_invoice):
        """Test the send_invoices management command"""
        from django.core.management import call_command
        from io import StringIO
        
        # Set order to confirmed status so it's eligible for invoice
        self.order_needs_confirmation.status = 'confirmed'
        self.order_needs_confirmation.save()
        
        mock_send_invoice.return_value = (True, "Invoice sent successfully")
        
        out = StringIO()
        call_command('send_invoices', '--dry-run', stdout=out)
        
        output = out.getvalue()
        
        # Should show the order that needs invoice
        self.assertIn('CMD-001', output)
        self.assertIn('DRY RUN', output)
        
        # Mock should not have been called in dry run
        mock_send_invoice.assert_not_called()

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SEND_ORDER_EMAILS=True
)
class EmailSignalsTestCase(TestCase):
    def setUp(self):
        """Set up test data for signal tests"""
        self.user = User.objects.create_user(
            username='signaluser',
            email='signal@example.com',
            first_name='Signal',
            last_name='User'
        )
        
        self.category = Category.objects.create(name='Signal Category')
        self.product = Product.objects.create(
            name='Signal Product',
            category=self.category,
            price=Decimal('200.00')
        )
    
    @patch('orders.signals.send_order_confirmation_delayed')
    def test_order_created_signal(self, mock_send_confirmation):
        """Test that order creation triggers confirmation email signal"""
        order = Order.objects.create(
            user=self.user,
            order_number='SIG-001',
            total_amount=Decimal('200.00'),
            final_amount=Decimal('200.00'),
            shipping_address='Signal Address',
            shipping_city='Signal City',
            shipping_state='Signal State',
            shipping_postal_code='11111',
            shipping_country='Signal Country'
        )
        
        # Signal should have scheduled the email sending
        # Note: The actual call happens on transaction commit, so we check if it was scheduled
        self.assertTrue(mock_send_confirmation.called)
    
    @patch('orders.signals.send_status_update_delayed')
    def test_order_status_change_signal(self, mock_send_status_update):
        """Test that order status change triggers status update email signal"""
        order = Order.objects.create(
            user=self.user,
            order_number='SIG-002',
            status='pending',
            total_amount=Decimal('150.00'),
            final_amount=Decimal('150.00'),
            shipping_address='Status Address',
            shipping_city='Status City',
            shipping_state='Status State',
            shipping_postal_code='22222',
            shipping_country='Status Country'
        )
        
        # Change status
        order.status = 'confirmed'
        order.save()
        
        # Signal should have been triggered
        self.assertTrue(mock_send_status_update.called)

class EmailTemplateTestCase(TestCase):
    """Test email template rendering"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='templateuser',
            email='template@example.com',
            first_name='Template',
            last_name='User'
        )
        
        self.category = Category.objects.create(name='Template Category')
        self.product = Product.objects.create(
            name='Template Product',
            category=self.category,
            price=Decimal('300.00')
        )
        
        self.order = Order.objects.create(
            user=self.user,
            order_number='TPL-001',
            status='confirmed',
            total_amount=Decimal('300.00'),
            final_amount=Decimal('300.00'),
            shipping_address='Template Street',
            shipping_city='Template City',
            shipping_state='Template State',
            shipping_postal_code='33333',
            shipping_country='Template Country'
        )
        
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('150.00'),
            size='L'
        )
    
    def test_order_confirmation_template_renders(self):
        """Test that order confirmation template renders without errors"""
        from django.template.loader import render_to_string
        
        context = {
            'order': self.order,
            'order_items': self.order.items.all(),
            'customer_name': 'Template User',
            'site_name': 'JOOG Wear',
            'site_url': 'https://example.com',
            'support_email': 'support@example.com'
        }
        
        # Test HTML template
        html_content = render_to_string('emails/order_confirmation.html', context)
        self.assertIn(self.order.order_number, html_content)
        self.assertIn('Template User', html_content)
        
        # Test text template
        text_content = render_to_string('emails/order_confirmation.txt', context)
        self.assertIn(self.order.order_number, text_content)
        self.assertIn('Template User', text_content)
    
    def test_tax_invoice_template_renders(self):
        """Test that tax invoice template renders without errors"""
        from django.template.loader import render_to_string
        from invoices.models import TaxInvoice
        
        invoice = TaxInvoice.objects.create(
            order=self.order,
            customer_name='Template User',
            customer_email='template@example.com',
            shipping_address=self.order.shipping_address,
            shipping_city=self.order.shipping_city,
            shipping_state=self.order.shipping_state,
            shipping_postal_code=self.order.shipping_postal_code,
            shipping_country=self.order.shipping_country,
            subtotal=Decimal('300.00'),
            final_amount=Decimal('354.00')  # With tax
        )
        
        context = {
            'order': self.order,
            'invoice': invoice,
            'customer_name': 'Template User',
            'site_name': 'JOOG Wear',
            'site_url': 'https://example.com',
            'support_email': 'support@example.com'
        }
        
        # Test HTML template
        html_content = render_to_string('emails/tax_invoice.html', context)
        self.assertIn(invoice.invoice_number, html_content)
        self.assertIn('Template User', html_content)
        
        # Test text template
        text_content = render_to_string('emails/tax_invoice.txt', context)
        self.assertIn(invoice.invoice_number, text_content)
        self.assertIn('Template User', text_content)