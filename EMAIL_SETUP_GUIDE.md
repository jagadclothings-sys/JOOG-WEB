# 📧 JOOG Wear Production Email Setup Guide

## 🎯 Current Status
- ✅ Development emails working (console only)
- ⚠️  Production emails need SMTP configuration
- ✅ Email templates ready and tested

## 🚀 Production Setup Options

### Option 1: Gmail SMTP (Recommended for Testing)

#### Step 1: Set up Gmail App Password
1. Go to your Gmail account settings
2. Enable 2-Factor Authentication
3. Generate an "App Password" for Django
4. Use this 16-digit password (not your regular Gmail password)

#### Step 2: Update .env file
```bash
# Enable production emails
USE_PRODUCTION_EMAIL=True

# Gmail SMTP settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-16-digit-app-password

# From addresses
DEFAULT_FROM_EMAIL=JOOG Wear <your-gmail@gmail.com>
ORDER_EMAIL_FROM=JOOG Wear <your-gmail@gmail.com>
```

### Option 2: SendGrid (Recommended for Production)

#### Step 1: Create SendGrid Account
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Get your API key
3. Verify your sender domain

#### Step 2: Install SendGrid
```bash
pip install sendgrid
```

#### Step 3: Update .env file
```bash
USE_PRODUCTION_EMAIL=True
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your_sendgrid_api_key
DEFAULT_FROM_EMAIL=JOOG Wear <contact@joogwear.com>
```

### Option 3: Custom SMTP Provider

#### For other providers (Mailgun, AWS SES, etc.)
```bash
USE_PRODUCTION_EMAIL=True
EMAIL_HOST=your-smtp-host.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=contact@joogwear.com
EMAIL_HOST_PASSWORD=your-smtp-password
```

## 📧 Domain Email Setup (contact@joogwear.com)

### Option A: Use your domain host's email service
1. Check if your domain provider offers email hosting
2. Create contact@joogwear.com mailbox
3. Get SMTP settings from your provider
4. Use those settings in your .env file

### Option B: Google Workspace
1. Sign up for Google Workspace
2. Add your domain (joogwear.com)
3. Create contact@joogwear.com account
4. Use Gmail SMTP settings with your custom email

### Option C: Microsoft 365
1. Sign up for Microsoft 365 Business
2. Add your domain
3. Create contact@joogwear.com
4. Use Outlook SMTP settings

## ⚡ Quick Test Setup (Gmail)

### 1. Create a Gmail account for testing
```
Email: joogwear.testing@gmail.com (or use your personal Gmail)
```

### 2. Enable App Password
- Go to Gmail Settings → Security
- Enable 2-Factor Authentication
- Create App Password for "Mail"

### 3. Update your .env file
```bash
USE_PRODUCTION_EMAIL=True
EMAIL_HOST_USER=joogwear.testing@gmail.com
EMAIL_HOST_PASSWORD=your-16-digit-app-password
DEFAULT_FROM_EMAIL=JOOG Wear <joogwear.testing@gmail.com>
ORDER_EMAIL_FROM=JOOG Wear <joogwear.testing@gmail.com>
```

### 4. Test the setup
```bash
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from JOOG Wear.',
    'joogwear.testing@gmail.com',
    ['your-email@gmail.com'],
    fail_silently=False,
)
```

## 🔒 Security Best Practices

### 1. Never commit .env file
Add to .gitignore:
```
.env
*.env
```

### 2. Use environment variables in production
For deployment platforms like Heroku, Railway, DigitalOcean:
- Set environment variables in your platform's dashboard
- Don't use .env file in production

### 3. Use different emails for different environments
- Development: console backend
- Staging: test email account
- Production: professional domain email

## 📊 Email Provider Comparison

| Provider | Cost | Setup Difficulty | Deliverability | Best For |
|----------|------|------------------|----------------|-----------|
| Gmail SMTP | Free (limited) | Easy | Good | Testing |
| SendGrid | Free tier, then paid | Medium | Excellent | Production |
| AWS SES | Pay-per-email | Hard | Excellent | High volume |
| Mailgun | Free tier, then paid | Medium | Excellent | Developers |

## 🚨 Common Issues & Solutions

### Issue: "Authentication failed"
- Check email/password are correct
- For Gmail: use App Password, not regular password
- Enable "Less secure apps" (not recommended) OR use App Password

### Issue: "Connection timed out"
- Check EMAIL_HOST and EMAIL_PORT
- Verify firewall settings
- Try different ports (587, 465, 25)

### Issue: Emails going to spam
- Set up SPF, DKIM, and DMARC records for your domain
- Use a reputable email service (SendGrid, etc.)
- Avoid spammy subject lines

### Issue: "Server does not support STARTTLS"
- Set EMAIL_USE_TLS = False and EMAIL_USE_SSL = True
- Or try different port (465 for SSL, 587 for TLS)

## 🧪 Testing Checklist

- [ ] Order confirmation emails sent to customers
- [ ] Admin notification emails sent to contact@joogwear.com
- [ ] Manual emails from admin panel working
- [ ] Email templates rendering correctly
- [ ] Unsubscribe links working (if implemented)
- [ ] Email deliverability tested (not in spam)

## 📞 Next Steps

1. **Choose your email provider** (Gmail for testing, SendGrid for production)
2. **Update your .env file** with the correct credentials
3. **Test email sending** with a real order
4. **Monitor email deliverability** and adjust if needed
5. **Set up domain authentication** (SPF/DKIM) for better deliverability