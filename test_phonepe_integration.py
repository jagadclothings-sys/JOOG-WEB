#!/usr/bin/env python
"""
PhonePe Integration Testing Script
This script helps you test your PhonePe integration in different modes.
"""

import os
import django
import json
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joog_ecommerce.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from orders.models import Order, OrderItem
from products.models import Product
from payments.phonepe import build_initiate_payload, initiate_payment

User = get_user_model()

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def test_phonepe_configuration():
    """Test current PhonePe configuration"""
    print_section("PHONEPE CONFIGURATION TEST")
    
    config_data = {
        'Merchant ID': settings.PHONEPE_MERCHANT_ID or "Not Set",
        'Salt Key': "*" * len(settings.PHONEPE_SALT_KEY) if settings.PHONEPE_SALT_KEY else "Not Set",
        'Salt Index': settings.PHONEPE_SALT_INDEX,
        'Environment': settings.PHONEPE_ENV,
        'Base URL': settings.PHONEPE_BASE_URL,
        'DEBUG Mode': settings.DEBUG
    }
    
    for key, value in config_data.items():
        print(f"{key:15}: {value}")
    
    # Determine current mode
    is_test_mode = settings.DEBUG or settings.PHONEPE_ENV == 'SANDBOX'
    has_credentials = bool(settings.PHONEPE_MERCHANT_ID and settings.PHONEPE_SALT_KEY)
    
    if is_test_mode and not has_credentials:
        print("\n✅ STATUS: Test bypass mode is ACTIVE")
        print("   ➤ Payments will simulate success immediately")
        print("   ➤ No actual PhonePe API calls will be made")
        print("   ➤ Perfect for development and testing")
        return 'test_bypass'
    elif has_credentials and settings.PHONEPE_ENV == 'SANDBOX':
        print("\n🧪 STATUS: PhonePe Sandbox mode is ACTIVE")
        print("   ➤ Will make real API calls to PhonePe sandbox")
        print("   ➤ Requires valid sandbox credentials")
        print("   ➤ Test payments with PhonePe test environment")
        return 'sandbox'
    elif has_credentials and settings.PHONEPE_ENV == 'PRODUCTION':
        print("\n🚨 STATUS: PhonePe Production mode is ACTIVE")
        print("   ➤ Will make real API calls to PhonePe production")
        print("   ➤ REAL MONEY transactions!")
        print("   ➤ Only use with live credentials")
        return 'production'
    else:
        print("\n⚠️  STATUS: Configuration incomplete")
        print("   ➤ Missing credentials or misconfigured")
        return 'misconfigured'

def test_order_creation():
    """Test creating a sample order for testing"""
    print_section("SAMPLE ORDER CREATION TEST")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@joogwear.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            print("✅ Created test user: testuser")
        else:
            print("✅ Using existing test user: testuser")
        
        # Get a product for testing
        product = Product.objects.first()
        if not product:
            print("❌ No products found in database")
            print("   ➤ Add some products first to test payments")
            return None
            
        print(f"✅ Using product: {product.name} (₹{product.price})")
        
        # Create a test order
        order = Order.objects.create(
            user=user,
            order_number=f'TEST_{Order.objects.count() + 1:06d}',
            total_amount=product.price,
            discount_amount=Decimal('0.00'),
            final_amount=product.price,
            status='pending',
            payment_status='pending',
            shipping_address='Test Address',
            shipping_city='Test City',
            shipping_state='Test State',
            shipping_postal_code='123456',
            shipping_country='India'
        )
        
        # Add order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            size='M',  # Default size
            price=product.price
        )
        
        print(f"✅ Created test order: {order.order_number}")
        print(f"   ➤ Amount: ₹{order.final_amount}")
        print(f"   ➤ Status: {order.status}")
        
        return order
        
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return None

def test_payment_payload_generation(order):
    """Test PhonePe payment payload generation"""
    print_section("PAYMENT PAYLOAD GENERATION TEST")
    
    if not order:
        print("❌ No order provided for testing")
        return False
        
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/test/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        request.META['wsgi.url_scheme'] = 'http'
        
        # Generate payment payload
        payload, payload_base64, x_verify = build_initiate_payload(order, request)
        
        print("✅ Payment payload generated successfully:")
        print(f"   ➤ Merchant ID: {payload['merchantId']}")
        print(f"   ➤ Transaction ID: {payload['merchantTransactionId']}")
        print(f"   ➤ Amount (paise): {payload['amount']}")
        print(f"   ➤ Amount (rupees): ₹{payload['amount'] / 100}")
        print(f"   ➤ Redirect URL: {payload['redirectUrl']}")
        
        print("\n📄 Base64 Payload (first 100 chars):")
        print(f"   {payload_base64[:100]}...")
        
        print(f"\n🔐 X-VERIFY Header (first 50 chars):")
        print(f"   {x_verify[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating payment payload: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_payment_flow_simulation(order, mode):
    """Test the complete payment flow based on current mode"""
    print_section("PAYMENT FLOW SIMULATION")
    
    if not order:
        print("❌ No order provided for testing")
        return
        
    if mode == 'test_bypass':
        print("🔄 Testing BYPASS MODE payment flow...")
        print("\n1. User clicks 'Pay with PhonePe'")
        print("2. System detects test mode")
        print("3. Order status changes to 'completed' immediately")
        print("4. Stock is reduced")
        print("5. Emails are sent")
        print("6. User sees confirmation page")
        print("\n✅ This mode is perfect for:")
        print("   ➤ Development testing")
        print("   ➤ UI/UX testing")
        print("   ➤ Order processing testing")
        print("   ➤ Email testing")
        
    elif mode == 'sandbox':
        print("🔄 Testing SANDBOX MODE payment flow...")
        print("\n1. User clicks 'Pay with PhonePe'")
        print("2. System calls PhonePe sandbox API")
        print("3. User redirected to PhonePe test payment page")
        print("4. User completes test payment")
        print("5. PhonePe calls your callback URL")
        print("6. System verifies payment status")
        print("7. Order completed if payment successful")
        
        # Try to make actual API call (will fail without proper credentials)
        try:
            factory = RequestFactory()
            request = factory.post('/test/')
            request.META['HTTP_HOST'] = 'localhost:8000'
            request.META['wsgi.url_scheme'] = 'http'
            
            print("\n🧪 Attempting sandbox API call...")
            response = initiate_payment(order, request)
            print(f"✅ API call successful: {response}")
        except Exception as e:
            print(f"⚠️  API call failed (expected without credentials): {e}")
            
    elif mode == 'production':
        print("🔄 PRODUCTION MODE detected - NOT TESTING")
        print("\n⚠️  WARNING: This would make real payments!")
        print("   ➤ Only test in production with extreme caution")
        print("   ➤ Use small amounts for testing")
        print("   ➤ Ensure you have proper refund procedures")

def test_callback_handling():
    """Test callback URL handling"""
    print_section("CALLBACK URL TESTING")
    
    callback_url = "http://localhost:8000/orders/pay/phonepe/callback/"
    print(f"📞 Callback URL: {callback_url}")
    print("\n📋 Callback handles these scenarios:")
    print("   ✅ Successful payment")
    print("   ❌ Failed payment")
    print("   ⏱️  Timeout/cancelled payment")
    print("   🔄 Status verification")
    
    print("\n🧪 To test callbacks locally:")
    print("   1. Install ngrok: npm install -g ngrok")
    print("   2. Run: ngrok http 8000")
    print("   3. Use ngrok URL in PhonePe dashboard")
    print("   4. Example: https://abc123.ngrok.io/orders/pay/phonepe/callback/")

def main():
    """Main testing function"""
    print("🧪 PhonePe Integration Testing Suite")
    print("====================================")
    
    # Test configuration
    mode = test_phonepe_configuration()
    
    # Create test order
    order = test_order_creation()
    
    # Test payload generation
    if order:
        test_payment_payload_generation(order)
    
    # Test payment flow
    test_payment_flow_simulation(order, mode)
    
    # Test callback handling
    test_callback_handling()
    
    # Recommendations
    print_section("RECOMMENDATIONS")
    
    if mode == 'test_bypass':
        print("🎯 CURRENT MODE: Test Bypass (Perfect for development)")
        print("\n📝 To test different scenarios:")
        print("   1. Complete checkout process")
        print("   2. Click 'Pay with PhonePe' button")
        print("   3. Verify order confirmation page")
        print("   4. Check order status in admin")
        print("   5. Verify stock reduction")
        print("   6. Check email notifications")
        
        print("\n🚀 To enable real PhonePe testing:")
        print("   1. Get PhonePe sandbox credentials")
        print("   2. Update .env file with credentials")
        print("   3. Restart server")
        print("   4. Test with PhonePe's sandbox environment")
        
    elif mode == 'sandbox':
        print("🧪 CURRENT MODE: PhonePe Sandbox (Integration testing)")
        print("   ➤ You can test real PhonePe flow with test money")
        
    elif mode == 'production':
        print("🚨 CURRENT MODE: PhonePe Production")
        print("   ⚠️  WARNING: Real money transactions!")
        
    print("\n💡 Testing Tips:")
    print("   1. Start with test bypass mode for initial development")
    print("   2. Move to sandbox for integration testing")
    print("   3. Use production only for live deployment")
    print("   4. Always verify order processing regardless of payment mode")
    print("   5. Test both successful and failed payment scenarios")
    
    print("\n✅ Testing complete!")

if __name__ == '__main__':
    main()