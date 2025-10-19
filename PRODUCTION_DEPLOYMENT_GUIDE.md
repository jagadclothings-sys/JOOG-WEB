# JOOG E-commerce Production Deployment Guide

## 🚀 Complete Production Checklist & Credentials

This guide covers everything needed to deploy your Django JOOG e-commerce application to production.

---

## 📋 **PRODUCTION REQUIREMENTS CHECKLIST**

### **1. SERVER & HOSTING REQUIREMENTS**

#### **Recommended Hosting Platforms:**
- **Cloud Platforms:** AWS, Google Cloud, DigitalOcean, Linode, Vultr
- **Platform as a Service:** Heroku, Railway, Render, PythonAnywhere
- **VPS Providers:** DigitalOcean Droplets, AWS EC2, Google Compute Engine

#### **Server Specifications (Minimum):**
- **RAM:** 2GB (4GB recommended)
- **Storage:** 20GB SSD (50GB+ recommended)
- **Bandwidth:** 1TB/month
- **OS:** Ubuntu 22.04 LTS, CentOS 8, or Debian 11

---

## 🔐 **REQUIRED CREDENTIALS & SERVICES**

### **1. DATABASE CREDENTIALS**
**Current:** SQLite (Development only)  
**Production Required:** PostgreSQL or MySQL

```bash
# PostgreSQL (Recommended)
DATABASE_NAME=joog_production
DATABASE_USER=joog_user
DATABASE_PASSWORD=secure_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**Setup Commands:**
```sql
-- PostgreSQL Setup
CREATE DATABASE joog_production;
CREATE USER joog_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE joog_production TO joog_user;
ALTER USER joog_user CREATEDB;
```

### **2. EMAIL SERVICE CREDENTIALS**
**Current:** Console backend (Development only)  
**Production Options:**

#### **Option A: Gmail SMTP (Small Scale)**
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-business-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

#### **Option B: Professional Email Service**
```bash
# GoDaddy Email
EMAIL_HOST=smtpout.secureserver.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=contact@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password

# Other providers
# Outlook: smtp-mail.outlook.com:587
# Yahoo: smtp.mail.yahoo.com:587
```

### **3. PAYMENT GATEWAY CREDENTIALS**
**Current:** PhonePe Integration

#### **PhonePe Production Credentials:**
```bash
PHONEPE_MERCHANT_ID=your-production-merchant-id
PHONEPE_SALT_KEY=your-production-salt-key
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=PRODUCTION
PHONEPE_BASE_URL=https://api.phonepe.com/apis/pg
```

**To Obtain:**
1. Sign up at [PhonePe Merchant Portal](https://www.phonepe.com/business/)
2. Complete KYC verification
3. Get production API credentials
4. Configure webhook URLs

### **4. DOMAIN & SSL CREDENTIALS**
```bash
# Domain Configuration
DOMAIN_NAME=yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# SSL Certificate (Let's Encrypt - Free)
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
```

### **5. GOOGLE OAUTH CREDENTIALS**
**For Social Login:**
```bash
GOOGLE_OAUTH2_CLIENT_ID=your-production-client-id.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your-production-client-secret
```

**Setup Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins

---

## ⚙️ **PRODUCTION CONFIGURATION FILES**

### **1. Production Settings File**
Create `settings_production.py`:

```python
from .settings import *
import dj_database_url

# Security Settings
DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# Static & Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Security Headers
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS Settings
USE_HTTPS = True

# Email Settings
USE_PRODUCTION_EMAIL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
```

### **2. Production Environment File (.env)**
```bash
# Production Environment Variables
DEBUG=False
SECRET_KEY=your-ultra-secure-secret-key-50-chars-minimum
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://joog_user:password@localhost:5432/joog_production

# Email Configuration
USE_PRODUCTION_EMAIL=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=contact@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=JOOG Wear <contact@yourdomain.com>
SERVER_EMAIL=JOOG Wear <admin@yourdomain.com>
ADMIN_EMAIL=admin@yourdomain.com
ORDER_EMAIL_FROM=JOOG Wear <orders@yourdomain.com>

# Company Information
SITE_NAME=JOOG Wear
COMPANY_LOGO_URL=https://yourdomain.com/static/img/joog-logo.png
COMPANY_ADDRESS=# 23/1, Ground Floor, Srinivasa Complex, 2nd Mn. CKC Garden, Mission Road, Bengaluru-560 027
COMPANY_PHONE=080 35910158
USE_HTTPS=True

# Payment Gateway
PHONEPE_MERCHANT_ID=your-production-merchant-id
PHONEPE_SALT_KEY=your-production-salt-key
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=PRODUCTION

# OAuth
GOOGLE_OAUTH2_CLIENT_ID=your-production-client-id.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your-production-client-secret

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 🐳 **DEPLOYMENT OPTIONS**

### **Option 1: Traditional VPS/Server Deployment**

#### **Required Software Stack:**
```bash
# System Requirements
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git
```

#### **Application Setup:**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/joog-ecommerce.git
cd joog-ecommerce

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary dj-database-url

# 4. Setup environment
cp .env.example .env
# Edit .env with production values

# 5. Database setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 6. Test application
gunicorn --bind 127.0.0.1:8000 joog_ecommerce.wsgi:application
```

#### **Nginx Configuration:**
```nginx
# /etc/nginx/sites-available/joog
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /path/to/joog-ecommerce/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/joog-ecommerce/mediafiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

#### **Supervisor Configuration:**
```ini
# /etc/supervisor/conf.d/joog.conf
[program:joog]
command=/path/to/joog-ecommerce/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 joog_ecommerce.wsgi:application
directory=/path/to/joog-ecommerce
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/joog/gunicorn.log
```

### **Option 2: Docker Deployment**

#### **Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "joog_ecommerce.wsgi:application"]
```

#### **docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: joog_production
      POSTGRES_USER: joog_user
      POSTGRES_PASSWORD: secure_password_here

  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/mediafiles
    environment:
      - DATABASE_URL=postgresql://joog_user:secure_password_here@db:5432/joog_production
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### **Option 3: Platform as a Service (Heroku)**

#### **Required Files:**

**Procfile:**
```
web: gunicorn joog_ecommerce.wsgi:application --log-file -
```

**runtime.txt:**
```
python-3.11.7
```

**Additional Requirements:**
```txt
# Add to requirements.txt
gunicorn==21.2.0
dj-database-url==2.1.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
```

#### **Heroku Configuration:**
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create joog-ecommerce

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=joog-ecommerce.herokuapp.com

# Add PostgreSQL
heroku addons:create heroku-postgresql:basic

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
heroku run python manage.py createsuperuser
```

---

## 🔒 **SECURITY CHECKLIST**

### **Essential Security Measures:**
- [ ] Change SECRET_KEY to strong 50+ character key
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure proper CORS settings
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

### **Additional Security (Recommended):**
- [ ] Rate limiting (django-ratelimit)
- [ ] CSRF protection verification
- [ ] SQL injection prevention
- [ ] XSS protection headers
- [ ] Content Security Policy
- [ ] Regular penetration testing

---

## 📊 **MONITORING & MAINTENANCE**

### **Essential Monitoring:**
```bash
# Log Files to Monitor
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/django/error.log
/var/log/postgresql/postgresql.log
```

### **Performance Monitoring Tools:**
- **Application:** New Relic, DataDog, Sentry
- **Server:** Uptime Robot, Pingdom
- **Database:** pgAdmin, phpMyAdmin

### **Backup Strategy:**
```bash
# Database Backup (Daily)
pg_dump joog_production > backup_$(date +%Y%m%d).sql

# Media Files Backup
rsync -av /path/to/mediafiles/ /backup/location/
```

---

## 🚀 **GO-LIVE CHECKLIST**

### **Pre-Launch:**
- [ ] All credentials configured
- [ ] Database migrated and populated
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] Email sending tested
- [ ] Payment gateway tested
- [ ] Admin user created
- [ ] Backup system operational
- [ ] Monitoring configured

### **Launch Day:**
- [ ] DNS records updated
- [ ] Application deployed
- [ ] All services running
- [ ] SSL working correctly
- [ ] Email notifications working
- [ ] Payment processing working
- [ ] All forms functional
- [ ] Mobile responsive
- [ ] Performance acceptable

### **Post-Launch:**
- [ ] Monitor error logs
- [ ] Test all major functionalities
- [ ] Monitor server resources
- [ ] Check email deliverability
- [ ] Verify payment processing
- [ ] Monitor site performance
- [ ] Set up automated backups

---

## 💰 **ESTIMATED COSTS (Monthly)**

### **Small Scale (0-1000 orders/month):**
- **Hosting:** $20-50 (DigitalOcean/Vultr)
- **Database:** Included or $15-25
- **Email Service:** $10-20 (Professional email)
- **SSL Certificate:** Free (Let's Encrypt)
- **Domain:** $10-15/year
- **Payment Gateway:** 2-3% per transaction
- **Total:** ~$40-95/month

### **Medium Scale (1000-10,000 orders/month):**
- **Hosting:** $50-150 (Multi-server setup)
- **Database:** $25-75 (Managed PostgreSQL)
- **Email Service:** $20-50
- **CDN:** $10-30 (Cloudflare/AWS)
- **Monitoring:** $20-50
- **Total:** ~$125-355/month

---

## 📞 **SUPPORT & CONTACTS**

### **Service Providers:**
- **Domain Registration:** GoDaddy, Namecheap, Google Domains
- **Hosting:** DigitalOcean, AWS, Google Cloud, Vultr
- **Email Services:** Gmail Business, Outlook 365, Zoho Mail
- **Payment Gateway:** PhonePe, Razorpay, Stripe
- **SSL Certificates:** Let's Encrypt (Free), Cloudflare

### **Emergency Contacts:**
- Server hosting support
- Domain registrar support
- Payment gateway support
- Email service support

---

## 📝 **FINAL NOTES**

1. **Start Small:** Begin with basic VPS hosting and scale as needed
2. **Test Everything:** Always test in staging before production
3. **Monitor Closely:** Keep close eye on logs first few weeks
4. **Have Backups:** Multiple backup strategies are essential
5. **Security First:** Never compromise on security measures
6. **Documentation:** Keep detailed records of all configurations

This guide provides everything needed to take your JOOG e-commerce application from development to production successfully.