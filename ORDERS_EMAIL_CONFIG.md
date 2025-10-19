# 📧 Email Configuration for orders@joogwear.com

## ✅ DJANGO CODE UPDATED!
Your Django project has been successfully updated to use `orders@joogwear.com` for all order-related emails.

---

## 📋 WHAT YOU NEED FROM GODADDY

### Step 1: Create Email Account
1. **Login to GoDaddy Account**
2. **Go to: My Products → Email & Office**
3. **Click: Manage** (next to your domain)
4. **Create New Email Account**:
   ```
   Email Address: orders@joogwear.com
   Password: [Create strong password - SAVE THIS!]
   Storage: At least 5GB
   ```

### Step 2: Copy These SMTP Settings

**GoDaddy SMTP Configuration:**
```
Host: smtpout.secureserver.net
Port: 587
Security: TLS (STARTTLS)
Username: orders@joogwear.com
Password: [The password you created above]
Authentication: Required
```

**Alternative SSL Settings (if TLS doesn't work):**
```
Host: smtpout.secureserver.net  
Port: 465
Security: SSL
Username: orders@joogwear.com
Password: [Same password]
```

---

## 🔧 WHERE TO CONFIGURE IN YOUR PROJECT

### Method 1: Create .env File (Recommended)

Create `.env` file in your project root:

```bash
# PRODUCTION EMAIL SETTINGS
USE_PRODUCTION_EMAIL=True

# GODADDY SMTP CONFIGURATION  
EMAIL_HOST=smtpout.secureserver.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=orders@joogwear.com
EMAIL_HOST_PASSWORD=YOUR_GODADDY_EMAIL_PASSWORD
EMAIL_TIMEOUT=60

# EMAIL ADDRESSES (Already updated in Django code)
DEFAULT_FROM_EMAIL=JOOG Wear <orders@joogwear.com>
ORDER_EMAIL_FROM=JOOG Wear <orders@joogwear.com>
SERVER_EMAIL=JOOG Wear <orders@joogwear.com>
ADMIN_EMAIL=orders@joogwear.com

# DJANGO SECURITY
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=joogwear.com,www.joogwear.com

# OTHER SETTINGS
SITE_NAME=JOOG Wear
COMPANY_NAME=JOOG
COMPANY_EMAIL=orders@joogwear.com
```

### Method 2: GoDaddy cPanel Environment Variables

**When deploying to GoDaddy, set these in cPanel → Python App → Environment Variables:**

| Variable Name | Value |
|---------------|-------|
| `EMAIL_HOST_USER` | `orders@joogwear.com` |
| `EMAIL_HOST_PASSWORD` | `your-godaddy-email-password` |
| `EMAIL_HOST` | `smtpout.secureserver.net` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `USE_PRODUCTION_EMAIL` | `True` |

---

## 🧪 TEST EMAIL CONFIGURATION

### Local Testing:
```bash
cd "C:\Users\Rohith\Downloads\JOOG web\project_3"
python manage.py shell
```

```python
from django.core.mail import send_mail

# Test email sending
send_mail(
    '[JOOG] Test Email Configuration', 
    'This email confirms orders@joogwear.com is working correctly!',
    'JOOG Wear <orders@joogwear.com>',
    ['your-personal-email@gmail.com'],
    fail_silently=False,
)
print("✅ Email sent successfully!")
```

---

## 📧 EMAIL TYPES SENT FROM orders@joogwear.com

### 1. Order Confirmation (to Customer)
- **Subject**: `[JOOG] Order Confirmation - #ORDER123`
- **From**: `JOOG Wear <orders@joogwear.com>`
- **Content**: Order details, payment info, shipping address

### 2. Admin Order Notification (to You)  
- **Subject**: `[JOOG] New Order Received - #ORDER123`
- **From**: `JOOG Wear <orders@joogwear.com>`
- **To**: `orders@joogwear.com`
- **Content**: New order alert with customer details

### 3. Order Status Updates (to Customer)
- **Subject**: `[JOOG] Your Order Status Updated - #ORDER123` 
- **From**: `JOOG Wear <orders@joogwear.com>`
- **Content**: Shipping updates, delivery confirmation

### 4. Tax Invoice Email (to Customer)
- **Subject**: `[JOOG] Tax Invoice - #INV123`
- **From**: `JOOG Wear <orders@joogwear.com>`
- **Attachment**: PDF invoice with GST breakdown

---

## ⚙️ FILES ALREADY UPDATED

✅ **settings.py** - All email defaults changed to `orders@joogwear.com`
✅ **Order confirmation emails** - Will use new email address
✅ **Admin notifications** - Will be sent from and to orders@joogwear.com  
✅ **Invoice emails** - Will use orders@joogwear.com
✅ **System emails** - Password resets, notifications, etc.

---

## 🚀 GODADDY DEPLOYMENT CHECKLIST

### Before Upload:
- [ ] Create `orders@joogwear.com` email account in GoDaddy
- [ ] Test email account can send/receive (send test email)
- [ ] Note down email password securely
- [ ] Create `.env` file with email settings

### After Upload to cPanel:
- [ ] Set environment variables in Python App settings
- [ ] Upload Django project files
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Migrate database: `python manage.py migrate`
- [ ] Test order email flow

### Final Testing:
- [ ] Place test order
- [ ] Verify customer receives confirmation email from orders@joogwear.com
- [ ] Check you receive admin notification at orders@joogwear.com
- [ ] Confirm emails are not going to spam

---

## ❗ IMPORTANT SECURITY NOTES

1. **Never commit email password to code**
2. **Use environment variables for sensitive data**
3. **Test email functionality before going live**
4. **Keep backup of email settings**
5. **Monitor email delivery and spam rates**

---

## 🔍 TROUBLESHOOTING

### Common Issues:

**"Authentication failed"**
- ✅ Double-check email password
- ✅ Verify email account is active
- ✅ Test login at GoDaddy webmail

**"Connection timeout"**
- ✅ Try port 465 with SSL instead
- ✅ Check hosting firewall settings

**Emails not sending**
- ✅ Verify `USE_PRODUCTION_EMAIL=True`
- ✅ Check Django error logs
- ✅ Test with simple send_mail() first

Your Django project is now fully configured to send all emails from **orders@joogwear.com**! 🎉