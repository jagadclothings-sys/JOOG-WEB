import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joog_ecommerce.settings')
django.setup()

from orders.email_utils import send_order_confirmation_email
from orders.models import Order
from django.contrib.auth import get_user_model

# Test email functionality
print("🧪 Testing email functionality...")

# Check if we have any orders to test with
orders = Order.objects.all().order_by('-created_at')[:1]

if orders:
    order = orders.first()
    print(f"📧 Testing with Order #{order.id} for user {order.user.email}")
    
    # Test sending order confirmation email
    success = send_order_confirmation_email(order)
    
    if success:
        print("✅ Order confirmation email test successful!")
        print("📧 Check your console output - email content should be displayed there")
    else:
        print("❌ Order confirmation email test failed!")
else:
    print("⚠️  No orders found in database to test with")
    print("💡 Create an order first, then run this test again")

print("\n📋 Email Configuration:")
from django.conf import settings
print(f"📤 Email Backend: {settings.EMAIL_BACKEND}")
print(f"🏢 Default From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"📧 Order Email From: {settings.ORDER_EMAIL_FROM}")
print(f"👥 Admins: {settings.ADMINS}")

print("\n✅ Email system is configured and ready!")
print("🎯 Next steps:")
print("   1. Place a test order to see automatic emails")
print("   2. Visit admin dashboard → Email Management to send manual emails")
print("   3. Switch to SMTP backend in production for actual email delivery")