# 🚀 Quick Email Setup (5 Minutes)

## 📋 Step-by-Step Instructions

### Step 1: Set up Gmail Account (2 minutes)
1. **Use existing Gmail** or create new account for testing
2. **Enable 2-Factor Authentication**:
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - Turn on 2-Step Verification

### Step 2: Generate App Password (1 minute)
1. **Go to App Passwords**:
   - Visit [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" as the app
   - Select "Other" and type "Django JOOG"
   - **Copy the 16-digit password** (format: xxxx xxxx xxxx xxxx)

### Step 3: Update Configuration (1 minute)
1. **Edit your `.env` file**:
   ```bash
   USE_PRODUCTION_EMAIL=True
   EMAIL_HOST_USER=your-actual-gmail@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   DEFAULT_FROM_EMAIL=JOOG Wear <your-actual-gmail@gmail.com>
   ORDER_EMAIL_FROM=JOOG Wear <your-actual-gmail@gmail.com>
   ```

### Step 4: Test Email Setup (1 minute)
1. **Run test script**:
   ```bash
   python test_email_setup.py
   ```
2. **Enter your email** when prompted
3. **Check your inbox** for test emails

## ✅ That's it! 

Your emails will now be sent to actual customer inboxes instead of just appearing in the console.

## 🔧 Alternative: Quick SendGrid Setup

If Gmail doesn't work, try SendGrid (free tier):

1. **Sign up** at [sendgrid.com](https://sendgrid.com)
2. **Get API key** from dashboard
3. **Update .env**:
   ```bash
   USE_PRODUCTION_EMAIL=True
   SENDGRID_API_KEY=your_api_key_here
   ```
4. **Install SendGrid**:
   ```bash
   pip install sendgrid
   ```

## 🚨 Common Issues

### Gmail "Authentication Failed"
- ✅ Use App Password (not regular password)
- ✅ Enable 2-Factor Authentication first
- ✅ Check email/password are correct

### Still Not Working?
1. Check spam folder
2. Try different Gmail account
3. Verify .env file is in project root
4. Restart Django server after changing .env

## 🎯 Next Steps After Testing

1. **For production**: Get domain email (contact@joogwear.com)
2. **For volume**: Switch to SendGrid/AWS SES
3. **For deliverability**: Set up SPF/DKIM records