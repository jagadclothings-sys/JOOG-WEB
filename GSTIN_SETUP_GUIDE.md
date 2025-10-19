# GSTIN Setup Guide for JOOG Billing System

## 🏢 Setting Up Your Actual GSTIN Number

This guide will help you configure your actual GSTIN number for proper GST billing in your JOOG e-commerce application.

---

## 📋 **What You Need**

### **1. Your Actual GSTIN Number**
- **Format**: 15-character alphanumeric code
- **Example Format**: `29ABCDE1234F1Z5`
- **Components**:
  - First 2 digits: State code (29 for Karnataka)
  - Next 10 characters: Entity identification
  - 13th character: Check sum
  - 14th character: Default 'Z'
  - 15th character: Check sum

### **2. Complete Company Information**
- Legal company name
- Registered address
- Contact phone number
- Business email
- Website URL

---

## ⚙️ **Configuration Steps**

### **Step 1: Update Your .env File**

Create or update your `.env` file with your actual business details:

```bash
# Company & GST Information
COMPANY_NAME=JAGAD CLOTHINGS
COMPANY_GSTIN=29XXXXXXXXXXXXXX  # Replace with your actual GSTIN
COMPANY_ADDRESS=# 23/1, Ground Floor, Srinivasa Complex, 2nd Mn. CKC Garden, Mission Road, Bengaluru-560 027
COMPANY_PHONE=080 35910158
COMPANY_EMAIL=contact@joogwear.com
COMPANY_WEBSITE=https://www.joogwear.com
```

**⚠️ Important**: Replace `29XXXXXXXXXXXXXX` with your actual 15-digit GSTIN number.

### **Step 2: Apply Database Migration**

Run the database migration to update the invoice model:

```bash
# Create migration for the model changes
python manage.py makemigrations invoices

# Apply the migration
python manage.py migrate
```

### **Step 3: Update Existing Invoices**

If you have existing invoices, update them with your new GSTIN:

```bash
# Dry run to see what would be updated (recommended first)
python manage.py update_gstin --gstin=YOUR_ACTUAL_GSTIN --dry-run

# Apply the update to all existing invoices
python manage.py update_gstin --gstin=YOUR_ACTUAL_GSTIN
```

**Alternative**: Update using .env settings:
```bash
# If GSTIN is set in .env file, you can run without --gstin parameter
python manage.py update_gstin
```

### **Step 4: Restart Your Application**

After updating the configuration, restart your Django application:

```bash
# Development server
python manage.py runserver

# Production server (if using gunicorn)
sudo systemctl restart your-app-name
```

---

## 🔍 **Verification Steps**

### **1. Check Invoice Generation**
1. Create a test order
2. Generate an invoice
3. Verify the invoice shows your correct GSTIN
4. Check that all company details appear correctly

### **2. Test Invoice Templates**
- **PDF Invoice**: Check `invoice_pdf.html`
- **Print Version**: Check `invoice_print_clean.html`
- **Email Template**: Check `invoice_email.html`
- **Tax Invoice Email**: Check `tax_invoice.html`

### **3. GST Calculation Verification**
Ensure GST is calculated correctly based on your state:
- **Intra-state (Karnataka to Karnataka)**: CGST + SGST (9% + 9% = 18%)
- **Inter-state (Karnataka to other states)**: IGST (18%)

---

## 🗂️ **Files That Will Show Your GSTIN**

### **Invoice Templates**
1. `invoices/templates/invoices/invoice_pdf.html`
2. `invoices/templates/invoices/invoice_print_clean.html` 
3. `invoices/templates/invoices/invoice_print_only.html`
4. `invoices/templates/invoices/invoice_email.html`
5. `templates/emails/tax_invoice.html`

### **Customer-Facing Pages**
1. `templates/accounts/admin_invoice_pdf.html`
2. `templates/accounts/customer_invoice_pdf.html`
3. `templates/accounts/customer_invoice_detail.html`

---

## 📊 **GSTIN Validation**

### **Manual Validation Checklist**
- [ ] GSTIN is exactly 15 characters
- [ ] Starts with correct state code (29 for Karnataka)
- [ ] No spaces or special characters
- [ ] Matches your GST registration certificate
- [ ] Appears on all generated invoices
- [ ] Shows in email notifications

### **Online GSTIN Verification**
You can verify your GSTIN at:
- **Official GST Portal**: https://www.gst.gov.in/
- **Search GSTIN**: Use "Search Taxpayer" feature
- **Verify Status**: Ensure your GSTIN is active

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Issue 1: GSTIN Not Appearing on Invoices**
**Solution**:
```bash
# Check if .env file is loaded
python manage.py shell
>>> from django.conf import settings
>>> print(settings.COMPANY_GSTIN)

# If empty, check your .env file and restart the server
```

#### **Issue 2: Old GSTIN Still Showing**
**Solution**:
```bash
# Update existing invoices
python manage.py update_gstin --gstin=YOUR_ACTUAL_GSTIN

# Clear any cached data
python manage.py collectstatic --clear
```

#### **Issue 3: Migration Errors**
**Solution**:
```bash
# Reset migrations if needed (BE CAREFUL - this will lose data)
python manage.py migrate invoices zero
python manage.py migrate invoices

# Or create a new migration
python manage.py makemigrations invoices --name update_gstin_fields
```

### **Debug Commands**
```bash
# Check current GSTIN in database
python manage.py shell
>>> from invoices.models import TaxInvoice
>>> invoice = TaxInvoice.objects.first()
>>> print(f"GSTIN: {invoice.company_gstin}")

# Test invoice generation
python manage.py shell
>>> from invoices.utils import generate_test_invoice
>>> generate_test_invoice()
```

---

## 🚨 **Security & Compliance**

### **Security Measures**
- ✅ Never commit GSTIN to version control
- ✅ Use environment variables for sensitive data
- ✅ Restrict access to `.env` files
- ✅ Regular backup of invoice data

### **GST Compliance**
- ✅ GSTIN matches GST registration
- ✅ Invoices have correct GST rates
- ✅ State-wise GST calculation is accurate
- ✅ Invoice numbers follow sequence
- ✅ All mandatory fields are present

### **Legal Requirements**
- ✅ Company name matches GST registration
- ✅ Address matches registered address
- ✅ GSTIN is displayed prominently
- ✅ Tax calculation is correct
- ✅ Invoice format follows GST rules

---

## 📞 **Support & Resources**

### **GST Resources**
- **GST Portal**: https://www.gst.gov.in/
- **GST Helpline**: 1800-103-4786
- **CBIC Website**: https://www.cbic.gov.in/

### **Technical Support**
If you face any technical issues:
1. Check Django logs for errors
2. Verify database connectivity
3. Test with a sample invoice
4. Contact your system administrator

---

## ✅ **Final Checklist**

Before going live, ensure:

### **Configuration**
- [ ] Actual GSTIN added to `.env` file
- [ ] Company details are correct
- [ ] Database migration applied
- [ ] Existing invoices updated
- [ ] Application restarted

### **Testing**
- [ ] Test invoice generation
- [ ] Verify GSTIN appears correctly
- [ ] Check GST calculations
- [ ] Test email notifications
- [ ] Validate PDF generation

### **Compliance**
- [ ] GSTIN matches registration certificate
- [ ] Address matches registered address
- [ ] Tax rates are correct
- [ ] Invoice format is compliant
- [ ] All mandatory fields present

---

## 📝 **Example Configuration**

Here's a complete example of how your `.env` file should look:

```bash
# Company & GST Configuration
COMPANY_NAME=JAGAD CLOTHINGS
COMPANY_GSTIN=29ABCDE1234F1Z5
COMPANY_ADDRESS=# 23/1, Ground Floor, Srinivasa Complex, 2nd Mn. CKC Garden, Mission Road, Bengaluru-560 027
COMPANY_PHONE=080 35910158
COMPANY_EMAIL=contact@joogwear.com  
COMPANY_WEBSITE=https://www.joogwear.com

# Other settings...
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Replace the example GSTIN `29ABCDE1234F1Z5` with your actual 15-digit GSTIN number.

---

**🎯 Result**: After completing this setup, all your invoices will display your actual GSTIN number and comply with GST regulations!