# 🎯 Influencer Credential Management System

This document explains how to create and manage influencer credentials for accessing order data through their coupon codes.

## 📋 Overview

The influencer system allows you to:
- Create secure credentials for influencers
- Assign coupon codes to specific influencers
- Give influencers access to view orders using their coupons
- Track performance and commission earnings
- Monitor login activity and usage

## 🚀 Quick Start

### 1. Create an Influencer

Use the management command to create a new influencer:

```bash
# Basic influencer creation
python manage.py create_influencer "Influencer Name" "email@example.com" "username123"

# Full featured creation
python manage.py create_influencer "Jane Smith" "jane@example.com" "janesmith" \
    --phone "+1234567890" \
    --instagram "janesmith" \
    --youtube "JaneSmithChannel" \
    --commission 5.0 \
    --coupon-codes JANE20 JANE30 \
    --notes "Top fashion influencer with 100K followers"
```

### 2. Generated Credentials

After creation, you'll get:
- **Username**: For login identification
- **API Key**: Secure authentication key (64 characters)
- **Dashboard URL**: Direct link for the influencer to access their data

### 3. Share Credentials

Provide the influencer with:
1. Their dashboard URL
2. Username and API key
3. Instructions on how to access their data

## 🔧 Administration

### Admin Panel Access

Go to `/admin/` and look for the **Influencers** section:

- **Influencers**: Manage influencer profiles and credentials
- **Influencer coupons**: Assign/manage coupon codes
- **Influencer login logs**: Monitor access activity

### Admin Features

#### Influencer Management:
- ✅ View total orders and revenue generated
- 🔄 Regenerate API keys for security
- 📊 Dashboard URL generation
- 🎯 Commission rate management
- 📱 Social media profile tracking

#### Coupon Assignment:
- Link coupons to specific influencers
- Track performance per coupon
- Set usage targets
- Add assignment notes

#### Security Monitoring:
- Login attempt tracking
- IP address logging
- User agent detection
- Success/failure monitoring

## 🔑 Credential Types

### 1. Username + API Key Authentication
- **Username**: Human-readable identifier
- **API Key**: 64-character secure token
- **Use**: Primary authentication method

### 2. Dashboard URL Authentication
- Pre-authenticated URL with embedded credentials
- One-click access for influencers
- Can be regenerated if compromised

## 🎯 Influencer Dashboard Features

Once logged in, influencers can see:
- Orders using their coupon codes
- Customer information (limited)
- Revenue generated
- Performance statistics
- Commission earnings
- Order history and trends

## 📊 Performance Tracking

### Metrics Available:
- **Total Orders**: Number of orders using influencer's coupons
- **Revenue Generated**: Total sales value from their coupons
- **Commission Earned**: Based on commission rate setting
- **Coupon Usage**: Individual coupon performance
- **Conversion Rates**: Success metrics

### Admin Reports:
- Individual influencer performance
- Comparative analysis
- Time-based trends
- Commission calculations

## 🔒 Security Features

### Authentication:
- Secure API key generation using `secrets` module
- Unique keys per influencer
- Key regeneration capability

### Access Control:
- Influencers only see orders with their coupon codes
- No access to other influencer data
- Limited customer information visibility

### Monitoring:
- All login attempts logged
- IP address tracking
- Failed login detection
- Session management

## 🛠️ Management Commands

### Create Influencer:
```bash
python manage.py create_influencer "Name" "email@example.com" "username" [options]
```

**Options:**
- `--phone`: Contact phone number
- `--instagram`: Instagram handle (without @)
- `--youtube`: YouTube channel name
- `--tiktok`: TikTok handle (without @)
- `--website`: Personal website URL
- `--commission`: Commission percentage (e.g., 5.0 for 5%)
- `--coupon-codes`: List of coupon codes to assign
- `--notes`: Admin notes about the influencer
- `--inactive`: Create as inactive influencer

### Examples:
```bash
# Basic creation
python manage.py create_influencer "John Doe" "john@example.com" "johndoe123"

# With social media and commission
python manage.py create_influencer "Jane Smith" "jane@example.com" "janesmith" \
    --instagram "janesmith" \
    --commission 7.5 \
    --coupon-codes JANE20 JANE30 SPECIAL50

# Inactive influencer
python manage.py create_influencer "Test User" "test@example.com" "testuser" --inactive
```

## 🎁 Coupon Integration

### Linking Coupons:
1. Create coupon codes in the Coupons admin
2. Use the management command with `--coupon-codes` option
3. Or assign via the admin panel under "Influencer coupons"

### Tracking:
- Each assigned coupon tracks usage automatically
- Revenue attribution per coupon
- Performance metrics per influencer-coupon pair

## 📈 Best Practices

### Security:
1. **Regenerate API keys** regularly for high-value influencers
2. **Monitor login logs** for suspicious activity
3. **Use HTTPS** in production for dashboard access
4. **Set appropriate commission rates** before going live

### Management:
1. **Clear naming conventions** for usernames
2. **Detailed notes** about each influencer
3. **Regular performance reviews** using admin reports
4. **Backup credential information** securely

### Communication:
1. **Clear instructions** when sharing credentials
2. **Test dashboard access** before sending to influencer
3. **Provide support contact** for technical issues
4. **Set expectations** about data availability

## 🔧 Troubleshooting

### Common Issues:

**Influencer can't access dashboard:**
- Check if influencer is active (`is_active = True`)
- Verify API key is correct
- Check URL formatting
- Review login logs for error details

**No orders showing:**
- Verify coupon codes are assigned to influencer
- Check if orders actually exist with those coupons
- Confirm payment status is 'completed'

**Credential management:**
- Use admin panel to regenerate API keys
- Update dashboard URLs after key regeneration
- Check for duplicate usernames or emails

## 📞 Support

For technical issues:
1. Check the admin panel login logs
2. Verify influencer and coupon assignments
3. Test dashboard access with fresh credentials
4. Review server logs for authentication errors

---

## 🎉 Sample Workflow

1. **Create influencer**: `python manage.py create_influencer "Sarah Fashion" "sarah@example.com" "sarahfashion" --instagram "sarahfashion" --commission 5.0`

2. **Get credentials**: Note the generated username, API key, and dashboard URL

3. **Assign coupons**: Either during creation or via admin panel

4. **Share access**: Send dashboard URL and credentials to influencer

5. **Monitor performance**: Use admin panel to track orders and revenue

6. **Calculate commissions**: Review earnings and process payments

That's it! Your influencer can now access their performance data through their secure dashboard.