# JOOG E-commerce Email Automation Setup

This document provides comprehensive setup instructions for the automated email system for order confirmations and tax invoices.

## 🚀 Quick Start

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your email settings in `.env`:**
   ```
   USE_PRODUCTION_EMAIL=True
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=your-business-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Test the setup:**
   ```bash
   python manage.py send_order_confirmations --dry-run
   ```

## 📧 Email Configuration

### Development Setup (Console Backend)
```python
USE_PRODUCTION_EMAIL=False
```
Emails will be printed to console for testing.

### Production Setup (SMTP)
```python
USE_PRODUCTION_EMAIL=True
EMAIL_HOST=smtp.gmail.com  # or your SMTP server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in `EMAIL_HOST_PASSWORD`

### Other Email Providers
- **Outlook/Hotmail:** `smtp-mail.outlook.com:587`
- **Yahoo:** `smtp.mail.yahoo.com:587`
- **Custom SMTP:** Use your provider's settings

## 🏗️ System Architecture

### Components Created

1. **Email Service (`orders/email_utils.py`)**
   - `EmailService` class for sending emails
   - Order confirmation emails
   - Tax invoice emails with PDF attachments
   - Status update emails
   - Error handling and retry logic

2. **Email Templates (`templates/emails/`)**
   - `order_confirmation.html/txt` - Order confirmation emails
   - `tax_invoice.html/txt` - Tax invoice emails
   - `order_status_update.html/txt` - Status update emails

3. **PDF Generation (`invoices/utils.py`)**
   - WeasyPrint (preferred)
   - ReportLab (fallback)
   - Professional invoice PDFs with GST compliance

4. **Database Fields (Order Model)**
   - `confirmation_email_sent` - Boolean flag
   - `confirmation_email_sent_at` - Timestamp
   - `confirmation_email_error` - Error messages
   - `invoice_email_sent` - Boolean flag
   - `invoice_email_sent_at` - Timestamp
   - `invoice_email_error` - Error messages

5. **Django Signals (`orders/signals.py`)**
   - Automatic email sending on order creation
   - Status update emails on order changes
   - Retry mechanism for failed emails
   - Error cleanup

6. **Management Commands**
   - `send_order_confirmations` - Bulk send confirmation emails
   - `send_invoices` - Bulk send invoice emails

## 🛠️ Management Commands

### Send Order Confirmation Emails
```bash
# Dry run (shows what would be sent)
python manage.py send_order_confirmations --dry-run

# Send up to 50 emails
python manage.py send_order_confirmations --limit 50

# Force resend even if already sent
python manage.py send_order_confirmations --force

# Send for specific order
python manage.py send_order_confirmations --order-id 123

# Only process orders from last 24 hours
python manage.py send_order_confirmations --max-age-hours 24
```

### Send Invoice Emails
```bash
# Dry run
python manage.py send_invoices --dry-run

# Send only for confirmed orders
python manage.py send_invoices --status confirmed

# Send for orders up to 7 days old
python manage.py send_invoices --max-age-days 7
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEND_ORDER_EMAILS` | `True` | Enable/disable automatic emails |
| `RETRY_FAILED_EMAILS` | `True` | Enable email retry mechanism |
| `EMAIL_RETRY_DELAY_HOURS` | `2` | Hours to wait before retry |
| `MAX_EMAIL_RETRIES` | `3` | Maximum retry attempts |
| `CLEANUP_EMAIL_ERRORS` | `True` | Clean up old error messages |
| `EMAIL_ERROR_RETENTION_DAYS` | `30` | Days to keep error messages |

### Company Information
```python
SITE_NAME=JOOG Wear
COMPANY_LOGO_URL=https://yourdomain.com/static/images/logo.png
COMPANY_ADDRESS=Your Company Address, City, State - Postal Code
COMPANY_PHONE=+1-234-567-8900
```

## 📊 Monitoring and Logging

### Log Files
- `logs/email.log` - Email sending logs
- View recent logs: `tail -f logs/email.log`

### Log Levels
- `INFO` - Successful operations
- `ERROR` - Failed operations
- `WARNING` - Retries and recoverable issues

### Admin Interface
Check order email status in Django admin:
- Order list shows email status columns
- Individual orders show detailed email information

## 🧪 Testing

### Run Email Tests
```bash
# Run all email tests
python manage.py test orders.tests.test_email_utils

# Run specific test class
python manage.py test orders.tests.test_email_utils.EmailServiceTestCase

# Test with coverage
coverage run --source='.' manage.py test orders.tests.test_email_utils
coverage report
```

### Test Email Sending
```bash
# Create a test order and send confirmation
python manage.py shell
>>> from orders.models import Order
>>> from orders.email_utils import EmailService
>>> order = Order.objects.first()
>>> service = EmailService()
>>> success, message = service.send_order_confirmation_email_new(order)
>>> print(f"Success: {success}, Message: {message}")
```

## 🚨 Troubleshooting

### Common Issues

1. **Emails not sending:**
   - Check `SEND_ORDER_EMAILS=True` in settings
   - Verify email credentials
   - Check spam folder
   - Review logs: `tail -f logs/email.log`

2. **PDF generation failing:**
   - Install WeasyPrint dependencies
   - Check ReportLab installation
   - Review invoice data completeness

3. **Template errors:**
   - Check template syntax
   - Verify context variables
   - Test template rendering in shell

4. **Gmail authentication:**
   - Use App Password, not regular password
   - Enable 2FA first
   - Check "Less secure app access" if needed

### Debug Mode
```python
# Enable debug logging
LOGGING['loggers']['orders.email_utils']['level'] = 'DEBUG'

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## 📈 Performance Optimization

### Async Processing (Optional)
```python
USE_CELERY_FOR_EMAILS=True
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Bulk Operations
- Use management commands for bulk sending
- Process emails in batches
- Monitor email sending rates

### Database Optimization
- Index email status fields
- Clean up old error messages
- Archive old orders

## 🔒 Security Considerations

1. **Email Credentials:**
   - Use environment variables
   - Never commit credentials to git
   - Use App Passwords for Gmail

2. **Email Content:**
   - Sanitize dynamic content
   - Validate email addresses
   - Implement rate limiting

3. **PDF Generation:**
   - Validate invoice data
   - Secure file storage
   - Clean up temporary files

## 🚀 Production Deployment

1. **Environment Setup:**
   ```bash
   USE_PRODUCTION_EMAIL=True
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Security Settings:**
   ```bash
   USE_HTTPS=True
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

3. **Monitoring:**
   - Set up log monitoring
   - Configure admin email notifications
   - Monitor email delivery rates

4. **Backup:**
   - Regular database backups
   - Email log backups
   - PDF file backups

## 📞 Support

For issues or questions:
1. Check the logs first: `logs/email.log`
2. Test with dry-run commands
3. Review Django admin for order email status
4. Check environment configuration

## 🔄 Regular Maintenance

### Daily Tasks
- Monitor email logs
- Check failed email retries
- Review order email status

### Weekly Tasks
- Clean up old log files
- Review email delivery rates
- Update email templates if needed

### Monthly Tasks
- Review and update email configurations
- Test backup and recovery procedures
- Optimize database performance

---

**Note:** This email automation system is production-ready and includes comprehensive error handling, logging, and monitoring capabilities. Follow the setup instructions carefully and test thoroughly before deployment.