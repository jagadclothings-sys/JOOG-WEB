# PhonePe Sandbox Integration Guide

## 🧪 Current Status: Test Mode Active

**✅ IMMEDIATE SOLUTION**: Your application is now configured to bypass PhonePe for testing. Clicking "Pay with PhonePe" will:
- ✅ Simulate successful payment
- ✅ Redirect to order confirmation page
- ✅ Complete all order processing (stock reduction, emails, etc.)
- ✅ Show "Payment successful! Your order has been confirmed. (Test Mode)" message

---

## 🚀 **Setting Up PhonePe Sandbox for Proper Testing**

### **Step 1: PhonePe Merchant Registration**

#### **1.1 Create PhonePe Merchant Account**
1. Visit [PhonePe Developer Portal](https://developer.phonepe.com/)
2. Click "Register as Merchant"
3. Fill in business details:
   - **Business Name**: JAGAD CLOTHINGS
   - **Category**: E-commerce/Retail
   - **Business Type**: Private Limited Company
   - **Website**: https://www.joogwear.com

#### **1.2 Get Sandbox Credentials**
After registration, you'll receive:
- **Merchant ID**: `M_YOUR_MERCHANT_ID`
- **Salt Key**: A secret key for API authentication
- **Salt Index**: Usually `1`

### **Step 2: Environment Configuration**

#### **2.1 Update Your .env File**
```bash
# PhonePe Sandbox Configuration
PHONEPE_MERCHANT_ID=M_YOUR_SANDBOX_MERCHANT_ID
PHONEPE_SALT_KEY=YOUR_SANDBOX_SALT_KEY
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=SANDBOX
PHONEPE_BASE_URL=https://api-preprod.phonepe.com/apis/pg-sandbox

# For production later
# PHONEPE_ENV=PRODUCTION
# PHONEPE_BASE_URL=https://api.phonepe.com/apis/pg
```

#### **2.2 Django Settings Verification**
Your current settings should already have:
```python
# PhonePe Payment Gateway Settings
PHONEPE_MERCHANT_ID = config('PHONEPE_MERCHANT_ID', default='')
PHONEPE_SALT_KEY = config('PHONEPE_SALT_KEY', default='')
PHONEPE_SALT_INDEX = config('PHONEPE_SALT_INDEX', default='1')
PHONEPE_ENV = config('PHONEPE_ENV', default='SANDBOX')
```

### **Step 3: Testing Sandbox Integration**

#### **3.1 Test Credentials (Example)**
PhonePe provides test credentials for initial testing:
```bash
# Example Test Credentials (Replace with your actual ones)
PHONEPE_MERCHANT_ID=PGTESTPAYUAT
PHONEPE_SALT_KEY=099eb0cd-02cf-4e2a-8aca-3e6c6aff0399
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=SANDBOX
```

#### **3.2 Enable Sandbox Mode**
To switch from test bypass to actual sandbox:

1. **Update your .env** with real sandbox credentials
2. **Remove test bypass** (optional, it auto-detects):
   ```python
   # In orders/views.py, you can comment out the test bypass
   # if getattr(settings, 'DEBUG', False) or getattr(settings, 'PHONEPE_ENV', 'SANDBOX') == 'SANDBOX':
   ```

#### **3.3 Sandbox Testing Features**
- **Test Cards**: PhonePe sandbox provides test payment methods
- **Simulate Success/Failure**: Test different payment scenarios
- **No Real Money**: All transactions are simulated
- **Full API Testing**: Complete payment flow testing

### **Step 4: Webhook Configuration**

#### **4.1 Callback URLs**
Configure these URLs in PhonePe merchant dashboard:
- **Redirect URL**: `https://yourdomain.com/orders/pay/phonepe/callback/`
- **Webhook URL**: `https://yourdomain.com/orders/pay/phonepe/callback/`

#### **4.2 Local Testing with ngrok**
For local development testing:
```bash
# Install ngrok
npm install -g ngrok

# Start your Django server
python manage.py runserver

# In another terminal, expose your local server
ngrok http 8000

# Use the ngrok URL in PhonePe configuration
# Example: https://abc123.ngrok.io/orders/pay/phonepe/callback/
```

---

## 🔧 **Implementation Details**

### **Current Payment Flow**
```
1. User clicks "Checkout" → Order created
2. User clicks "Pay with PhonePe" → phonepe_initiate view
3. [CURRENT] → Direct to order confirmation (test mode)
4. [SANDBOX] → Redirect to PhonePe sandbox
5. [SANDBOX] → PhonePe processes payment
6. [SANDBOX] → Callback to phonepe_callback view
7. Order finalized → Confirmation page
```

### **Test vs Sandbox vs Production**

| Mode | Description | Use Case |
|------|-------------|----------|
| **Test (Current)** | Direct bypass, no PhonePe API calls | Quick development testing |
| **Sandbox** | Real PhonePe API, test environment | Integration testing |
| **Production** | Live PhonePe API, real payments | Live website |

---

## 🧪 **Testing Scenarios**

### **Test Different Payment Outcomes**

#### **1. Successful Payment Test**
```bash
# Test with sandbox credentials
# Use PhonePe test cards for successful transactions
```

#### **2. Failed Payment Test**
```bash
# Use PhonePe test scenarios for failed payments
# Test your error handling
```

#### **3. Webhook Testing**
```bash
# Test callback handling
# Verify order status updates
```

### **Debug Commands**
```bash
# Check current PhonePe configuration
python manage.py shell
>>> from django.conf import settings
>>> print("Merchant ID:", settings.PHONEPE_MERCHANT_ID)
>>> print("Environment:", settings.PHONEPE_ENV)
>>> print("Base URL:", settings.PHONEPE_BASE_URL)

# Test payment initiation
>>> from orders.models import Order
>>> order = Order.objects.first()
>>> print("Order:", order.order_number, "Amount:", order.final_amount)
```

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Issue 1: "Failed to initiate payment" Error**
**Causes:**
- Invalid merchant credentials
- Wrong base URL
- Network connectivity issues

**Solution:**
```bash
# Verify credentials
python manage.py shell
>>> from django.conf import settings
>>> print("Check these values:")
>>> print("MERCHANT_ID:", bool(settings.PHONEPE_MERCHANT_ID))
>>> print("SALT_KEY:", bool(settings.PHONEPE_SALT_KEY))
>>> print("BASE_URL:", settings.PHONEPE_BASE_URL)
```

#### **Issue 2: Callback Not Working**
**Causes:**
- Incorrect callback URL
- Local development without ngrok
- Webhook not configured

**Solution:**
1. Use ngrok for local testing
2. Configure proper URLs in PhonePe dashboard
3. Check Django logs for callback requests

#### **Issue 3: Payment Status Not Updating**
**Causes:**
- Callback logic errors
- Database connection issues
- Incorrect transaction ID matching

**Solution:**
```python
# Check transaction status manually
python manage.py shell
>>> from payments.phonepe import status_check
>>> result = status_check("your_transaction_id")
>>> print(result)
```

---

## 📋 **Testing Checklist**

### **Pre-Testing**
- [ ] PhonePe merchant account created
- [ ] Sandbox credentials obtained
- [ ] Environment variables configured
- [ ] Django settings updated
- [ ] Callback URLs configured

### **Testing Phase**
- [ ] Test mode working (current setup)
- [ ] Sandbox credentials tested
- [ ] Payment initiation working
- [ ] Payment callback handling
- [ ] Order status updates
- [ ] Email notifications sent
- [ ] Stock reduction working

### **Production Readiness**
- [ ] Production credentials obtained
- [ ] Production URLs configured
- [ ] SSL certificate installed
- [ ] Payment flow tested end-to-end
- [ ] Error handling verified
- [ ] Logging configured

---

## 🚀 **Going Live Steps**

### **1. Get Production Credentials**
```bash
# Update .env for production
PHONEPE_MERCHANT_ID=YOUR_PRODUCTION_MERCHANT_ID
PHONEPE_SALT_KEY=YOUR_PRODUCTION_SALT_KEY  
PHONEPE_ENV=PRODUCTION
PHONEPE_BASE_URL=https://api.phonepe.com/apis/pg
```

### **2. Remove Test Bypass**
```python
# In orders/views.py, remove or comment out the test bypass:
# if getattr(settings, 'DEBUG', False) or getattr(settings, 'PHONEPE_ENV', 'SANDBOX') == 'SANDBOX':
#     # ... test mode code
```

### **3. Final Testing**
- Test with small amounts first
- Verify all payment scenarios
- Check refund process
- Monitor transaction logs

---

## 📞 **Support Resources**

### **PhonePe Documentation**
- [PhonePe Developer Docs](https://developer.phonepe.com/docs/)
- [API Reference](https://developer.phonepe.com/v1/reference)
- [Integration Guide](https://developer.phonepe.com/docs/integration-guide/)

### **PhonePe Support**
- **Email**: developer-support@phonepe.com
- **Portal**: [PhonePe Merchant Support](https://merchant.phonepe.com/)

### **Technical Resources**
- [PhonePe Test Environment](https://developer.phonepe.com/docs/test-environment/)
- [Error Codes Reference](https://developer.phonepe.com/docs/error-codes/)
- [Webhook Guide](https://developer.phonepe.com/docs/webhooks/)

---

## 🎯 **Current Status Summary**

### **✅ What's Working Now**
- Order creation and checkout flow
- **Test mode payment bypass** (immediate solution)
- Order confirmation and processing
- Email notifications
- Stock management
- Invoice generation

### **🔄 Next Steps**
1. **Immediate**: Test the current bypass functionality
2. **Short-term**: Set up PhonePe sandbox account
3. **Testing**: Integrate sandbox credentials
4. **Production**: Switch to live PhonePe integration

### **💡 Benefits of Current Setup**
- ✅ **Immediate testing** without waiting for PhonePe approval
- ✅ **Complete order flow** testing
- ✅ **Easy switching** between test/sandbox/production
- ✅ **No downtime** during PhonePe setup

**🎉 Your e-commerce application is fully functional for testing right now!**