# 🚀 GoDaddy Professional Email Setup for JOOG Wear

## Overview
This guide will help you integrate your GoDaddy professional email with JOOG Wear for sending order confirmations and tax invoices.

## Prerequisites
- GoDaddy Professional Email account
- Your domain purchased through GoDaddy
- Professional email addresses already created (e.g., orders@yourdomain.com)

## Step 1: GoDaddy Email Configuration

### 1.1 Create Professional Email Accounts
In your GoDaddy dashboard, create these email accounts:
- `orders@yourdomain.com` - For order confirmations
- `admin@yourdomain.com` - For admin notifications
- `contact@yourdomain.com` - For general contact

### 1.2 Get SMTP Settings
GoDaddy uses these SMTP settings:
- **SMTP Server:** `smtpout.secureserver.net`
- **Port:** `587` (TLS) or `465` (SSL)
- **Authentication:** Required
- **Encryption:** TLS (preferred) or SSL

## Step 2: Configure Django Settings

### 2.1 Update .env File
Edit your `.env` file with your GoDaddy email credentials:

```env
# Enable production email sending
USE_PRODUCTION_EMAIL=True

# GoDaddy SMTP Settings
EMAIL_HOST=smtpout.secureserver.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Your GoDaddy Professional Email Credentials
# REPLACE WITH YOUR ACTUAL CREDENTIALS:
EMAIL_HOST_USER=orders@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password

# Professional Email Display Settings
# REPLACE yourdomain.com WITH YOUR ACTUAL DOMAIN:
DEFAULT_FROM_EMAIL=JOOG Wear <orders@yourdomain.com>
ORDER_EMAIL_FROM=JOOG Wear <orders@yourdomain.com>
SERVER_EMAIL=JOOG Wear <admin@yourdomain.com>
ADMIN_EMAIL=admin@yourdomain.com
```

**🔴 Important:** Replace `yourdomain.com` with your actual domain and use your real email passwords!

### 2.2 Alternative SSL Configuration
If TLS doesn't work, try SSL:

```env
EMAIL_HOST=smtpout.secureserver.net
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

## Step 3: Test Email Configuration

### 3.1 Test Basic Email Sending

```bash
python manage.py shell
```

In Django shell:

```python
from django.core.mail import send_mail
from django.conf import settings

# Test email sending
result = send_mail(
    'Test Email from JOOG Wear',
    'This email confirms your GoDaddy integration is working!',
    settings.DEFAULT_FROM_EMAIL,
    ['your-personal-email@gmail.com'],  # Use your personal email
    fail_silently=False,
)
print(f"Email sent successfully: {result}")
```

### 3.2 Test Order Email Flow
Place a test order on your website and verify:
- ✅ Customer receives order confirmation email
- ✅ Admin receives order notification
- ✅ Tax invoice is attached (if generated)

## Step 4: Email Features Overview

### 4.1 Order Confirmation Emails
- **Sent to:** Customer's email
- **Includes:** Order details, items, pricing, shipping address
- **Branding:** Professional JOOG Wear HTML template
- **Attachment:** Tax invoice PDF (when available)

### 4.2 Admin Notification Emails
- **Sent to:** `admin@yourdomain.com`
- **Includes:** New order alerts, customer information
- **Purpose:** Quick order processing notifications

### 4.3 Tax Invoice Integration
- **Format:** Professional PDF with GST calculations
- **Content:** Company details, customer info, itemized billing
- **Delivery:** Automatically attached to customer emails

## Step 5: Troubleshooting

### 5.1 Common Issues

#### "Authentication failed" Error
- ✅ Verify email and password are correct
- ✅ Test login at GoDaddy webmail
- ✅ Ensure email account is active
- ✅ Check for typos in .env file

#### "Connection timeout" Error
- ✅ Try port 465 with SSL instead of 587 with TLS
- ✅ Check server firewall settings
- ✅ Verify hosting provider allows SMTP connections

#### Emails not being sent
- ✅ Confirm `USE_PRODUCTION_EMAIL=True`
- ✅ Check Django logs for error messages
- ✅ Test with simple send_mail() first
- ✅ Verify .env file is being loaded

### 5.2 Debugging Steps

1. **Check Django Logs:**
```bash
tail -f email.log
```

2. **Test SMTP Connection:**
```python
import smtplib
server = smtplib.SMTP('smtpout.secureserver.net', 587)
server.starttls()
server.login('your-email@yourdomain.com', 'your-password')
print("SMTP connection successful!")
server.quit()
```

3. **Verify Settings Loading:**
```python
from django.conf import settings
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Use Production: {settings.USE_PRODUCTION_EMAIL}")
```

## Step 6: Production Deployment

### 6.1 Security Checklist
- [ ] Email passwords are not in version control
- [ ] .env file is added to .gitignore
- [ ] Production uses environment variables (not .env)
- [ ] Email credentials are stored securely

### 6.2 Performance Optimization
- [ ] Email sending is asynchronous (consider Celery for high volume)
- [ ] Error handling implemented for failed sends
- [ ] Logging configured for monitoring
- [ ] Rate limiting considered if needed

## Step 7: Email Deliverability

### 7.1 Domain Authentication
Set up these DNS records for better deliverability:
- **SPF Record:** Add to DNS
- **DKIM:** Configure in GoDaddy email settings
- **DMARC:** Set up domain policy

### 7.2 Best Practices
- Use consistent "From" names and addresses
- Include unsubscribe links where required
- Monitor bounce rates and spam complaints
- Keep email content professional and relevant

## Step 8: Monitoring and Maintenance

### 8.1 Email Logging
Monitor `email.log` for:
- Successful sends
- Failed attempts
- Authentication errors
- Performance issues

### 8.2 Regular Testing
- Monthly: Test order email flow
- After updates: Verify email functionality
- Before campaigns: Check deliverability

## 🆘 Support Resources

### GoDaddy Support
- GoDaddy Help Center: Email configuration guides
- Contact: GoDaddy technical support for SMTP issues

### Django Documentation
- Email backend configuration
- SMTP troubleshooting guides

### Quick Contact
If you need help with this setup:
1. Check GoDaddy email account status
2. Verify domain MX records
3. Test SMTP credentials in webmail first
4. Review Django email backend documentation

---

**✅ Success Indicator:** When customers place orders, they should receive professional branded emails from your domain (orders@yourdomain.com) with tax invoice attachments!