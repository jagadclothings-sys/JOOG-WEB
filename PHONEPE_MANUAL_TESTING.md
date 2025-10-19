# PhonePe Manual Testing Guide

## 🎯 Current Status: Test Mode Active

Your PhonePe integration is currently in **TEST BYPASS MODE**, which is perfect for development and testing. Here's how to test it manually.

## ✅ How Your PhonePe Integration Currently Works

### Test Mode Behavior
- **Status**: Test bypass mode is ACTIVE
- **Merchant ID**: Not set (using default empty)
- **Salt Key**: Not set (using default empty)
- **Environment**: SANDBOX
- **DEBUG Mode**: True

### What Happens When User Pays
1. User adds items to cart
2. User goes through checkout process
3. User clicks "Pay with PhonePe" button
4. **System automatically simulates successful payment** (no PhonePe API call)
5. Order status changes to "completed"
6. Stock is reduced
7. Order confirmation emails are sent
8. User sees "Payment successful! Your order has been confirmed. (Test Mode)" message
9. User is redirected to order confirmation page

## 🧪 Manual Testing Steps

### 1. Test Complete Order Flow
```bash
# Start the server
python manage.py runserver

# Open browser to: http://localhost:8000
```

### 2. Create a Test Order
1. Browse products on the homepage
2. Add a product to cart
3. Go to cart page
4. Click "Checkout"
5. Fill in shipping information
6. Click "Place Order"

### 3. Test Payment Flow
1. On payment page, click "Pay with PhonePe"
2. **Expected Result**: Immediate redirect to confirmation page
3. **Expected Message**: "Payment successful! Your order has been confirmed. (Test Mode)"
4. **Order Status**: Should be "completed" in admin

### 4. Verify Order Processing
1. Check admin panel: `/admin/`
2. Go to Orders section
3. Find your test order
4. Verify:
   - Status: "completed"
   - Payment status: "completed"
   - PhonePe transaction ID: Shows test transaction

### 5. Test Stock Reduction
1. Check product stock before ordering
2. Complete an order
3. Verify stock is reduced by order quantity

### 6. Test Email Notifications
- Order confirmation email (to customer)
- Order notification email (to admin)
- Check console output for email logs

## 🔧 Testing Different Scenarios

### Scenario 1: Basic Product Order
- Order a single product
- Verify complete flow

### Scenario 2: Multiple Items Order
- Add multiple products to cart
- Test bulk order processing

### Scenario 3: User Account Integration
- Create user account
- Login and place order
- Check order history

### Scenario 4: Address Management
- Add multiple addresses
- Select different shipping address
- Verify address handling

## 📊 What to Monitor

### Success Indicators
- ✅ Order created successfully
- ✅ Payment marked as "completed"
- ✅ Stock reduced correctly
- ✅ Emails sent successfully
- ✅ User redirected to confirmation
- ✅ Order shows in admin panel

### Failure Indicators
- ❌ Order stuck in "pending" status
- ❌ Payment status remains "pending"
- ❌ Stock not reduced
- ❌ No confirmation emails
- ❌ User sees error messages

## 🚀 Advanced Testing

### Test with Different Users
1. Create multiple user accounts
2. Test ordering as different users
3. Verify user isolation

### Test Admin Functions
1. Login to admin panel
2. View orders list
3. Update order statuses
4. Test order management

### Test Error Conditions
1. Order with out-of-stock items
2. Invalid shipping information
3. System errors (by temporarily breaking configuration)

## 🔄 Switching to Real PhonePe Testing

When you're ready to test with actual PhonePe API:

### 1. Get PhonePe Sandbox Credentials
- Visit [PhonePe Developer Portal](https://developer.phonepe.com/)
- Register as merchant
- Get sandbox credentials

### 2. Update Environment Variables
```bash
# Create .env file or update existing
PHONEPE_MERCHANT_ID=your_sandbox_merchant_id
PHONEPE_SALT_KEY=your_sandbox_salt_key
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=SANDBOX
```

### 3. Restart Server
```bash
python manage.py runserver
```

### 4. Test with Real API
- Now payments will use actual PhonePe sandbox
- Users will be redirected to PhonePe test environment
- You can test with PhonePe's test cards

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Order not completing
- **Solution**: Check admin logs, verify user authentication

**Issue**: Emails not sending
- **Solution**: Check email backend configuration in settings

**Issue**: Stock not reducing
- **Solution**: Verify product stock management in models

**Issue**: User not redirected
- **Solution**: Check URL configurations and view logic

### Debug Commands
```bash
# Check current configuration
python check_phonepe_config.py

# Run comprehensive tests
python test_phonepe_integration.py

# Check Django logs
python manage.py runserver --verbosity=2
```

## 📋 Test Checklist

### Basic Functionality
- [ ] Homepage loads correctly
- [ ] Product listing works
- [ ] Add to cart functions
- [ ] Cart displays correctly
- [ ] Checkout form works
- [ ] Order creation succeeds
- [ ] Payment simulation works
- [ ] Confirmation page shows
- [ ] Order appears in admin

### Advanced Features
- [ ] User registration/login
- [ ] Address management
- [ ] Order history
- [ ] Email notifications
- [ ] Stock management
- [ ] Admin order management

## 💡 Tips for Testing

1. **Use realistic data**: Test with actual product names, addresses, and user information
2. **Test edge cases**: Empty cart, invalid addresses, special characters
3. **Monitor logs**: Watch console output for errors and warnings
4. **Test different browsers**: Ensure compatibility across browsers
5. **Test mobile view**: Verify responsive design
6. **Clear cache**: Clear browser cache between tests for accurate results

## ✅ Test Results Template

```
Date: ___________
Tester: ___________

Basic Flow:
- [ ] Product selection: Pass/Fail
- [ ] Cart functionality: Pass/Fail
- [ ] Checkout process: Pass/Fail
- [ ] Payment simulation: Pass/Fail
- [ ] Order completion: Pass/Fail

Advanced Features:
- [ ] User management: Pass/Fail
- [ ] Email notifications: Pass/Fail
- [ ] Stock management: Pass/Fail
- [ ] Admin functions: Pass/Fail

Issues Found:
1. ________________________________
2. ________________________________
3. ________________________________

Overall Status: Pass/Fail
```

---

**Current Status**: Your PhonePe integration is working perfectly in test mode and ready for development testing! 🎉