#!/usr/bin/env python
"""
JOOG Wear Email Configuration Test Script

This script helps you test your email configuration before deploying to production.
Run this after setting up your .env file with email credentials.
"""

import os
import django
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joog_ecommerce.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from orders.models import Order

def test_email_configuration():
    """Test basic email configuration"""
    print("🧪 Testing JOOG Wear Email Configuration...")
    print("=" * 50)
    
    # Display current settings
    print(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"🏠 Email Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"🔌 Email Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"👤 Email User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"🔐 Password Set: {'Yes' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'No'}")
    print(f"🔒 TLS Enabled: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    print(f"📮 Default From: {settings.DEFAULT_FROM_EMAIL}")
    print()

def send_test_email(recipient_email):
    """Send a simple test email"""
    try:
        print(f"📤 Sending test email to {recipient_email}...")
        
        subject = "[JOOG Test] Email Configuration Test"
        message = f"""
Hello!

This is a test email from your JOOG Wear e-commerce platform.

✅ Email configuration is working correctly!

Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
JOOG Wear System
"""
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}")
        return False

def test_order_email_template(recipient_email):
    """Test the actual order confirmation email template"""
    try:
        print(f"📧 Testing order confirmation template to {recipient_email}...")
        
        # Get the most recent order for testing
        recent_order = Order.objects.order_by('-created_at').first()
        
        if not recent_order:
            print("⚠️  No orders found in database. Please create a test order first.")
            return False
        
        # Import email function
        from orders.email_utils import send_order_confirmation_email
        
        # Send the email
        success = send_order_confirmation_email(recent_order)
        
        if success:
            print("✅ Order confirmation email template test successful!")
            return True
        else:
            print("❌ Order confirmation email template test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test order email template: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 JOOG Wear Email System Test")
    print("=" * 50)
    
    # Check if we're using production email
    use_production = getattr(settings, 'USE_PRODUCTION_EMAIL', False)
    
    if not use_production:
        print("⚠️  Currently using DEVELOPMENT mode (console backend)")
        print("   Emails will appear in console, not sent to recipients.")
        print("   To test real emails, set USE_PRODUCTION_EMAIL=True in .env")
        print()
    else:
        print("✅ Using PRODUCTION email mode (SMTP backend)")
        print("   Emails will be sent to actual recipients.")
        print()
    
    # Display configuration
    test_email_configuration()
    
    if use_production:
        # Get recipient email
        recipient = input("Enter your email address to receive test emails: ").strip()
        
        if not recipient:
            print("❌ No email address provided. Exiting.")
            return
        
        print()
        
        # Run tests
        print("Running Email Tests...")
        print("-" * 30)
        
        # Test 1: Simple email
        simple_test = send_test_email(recipient)
        
        print()
        
        # Test 2: Order confirmation template
        template_test = test_order_email_template(recipient)
        
        print()
        print("📊 Test Results:")
        print(f"   Simple Email: {'✅ PASS' if simple_test else '❌ FAIL'}")
        print(f"   Order Template: {'✅ PASS' if template_test else '❌ FAIL'}")
        
        if simple_test and template_test:
            print("\n🎉 All tests passed! Your email system is ready for production.")
        else:
            print("\n⚠️  Some tests failed. Please check your email configuration.")
            print("   Refer to EMAIL_SETUP_GUIDE.md for troubleshooting.")
    
    else:
        print("To test actual email delivery:")
        print("1. Update your .env file with email credentials")
        print("2. Set USE_PRODUCTION_EMAIL=True")
        print("3. Run this script again")

if __name__ == "__main__":
    main()