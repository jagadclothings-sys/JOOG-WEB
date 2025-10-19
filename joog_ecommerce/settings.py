import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

DEBUG = True

ALLOWED_HOSTS = []

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'accounts',
    'products',
    'orders',
    'coupons',
    'invoices',
    'influencers',  # New influencer management app
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'joog_ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.categories',
                'orders.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'joog_ecommerce.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Indian Standard Time (IST)
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
CSRF_COOKIE_SECURE = False     # Set True in production with HTTPS

# PhonePe Payment Gateway Settings
PHONEPE_MERCHANT_ID = config('PHONEPE_MERCHANT_ID', default='')
PHONEPE_SALT_KEY = config('PHONEPE_SALT_KEY', default='')
PHONEPE_SALT_INDEX = config('PHONEPE_SALT_INDEX', default='1')
PHONEPE_ENV = config('PHONEPE_ENV', default='SANDBOX')  # SANDBOX or PRODUCTION
# Default to sandbox base URL unless explicitly overridden
PHONEPE_BASE_URL = config(
    'PHONEPE_BASE_URL',
    default='https://api-preprod.phonepe.com/apis/pg-sandbox'
) if PHONEPE_ENV.upper() == 'SANDBOX' else config(
    'PHONEPE_BASE_URL',
    default='https://api.phonepe.com/apis/pg'
)

CORS_ALLOW_ALL_ORIGINS = True

# Django Allauth Configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth Settings (Updated for Django 5.2+)
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Changed from 'mandatory' to avoid email verification issues
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

# Social Account Settings
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True

# Google OAuth Settings
GOOGLE_OAUTH2_CLIENT_ID = config('GOOGLE_OAUTH2_CLIENT_ID', default='your-google-client-id')
GOOGLE_OAUTH2_CLIENT_SECRET = config('GOOGLE_OAUTH2_CLIENT_SECRET', default='your-google-client-secret')

# Social Account Providers Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Custom Adapters
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# Email Configuration - Production Ready
# Choose your email backend based on environment
USE_PRODUCTION_EMAIL = config('USE_PRODUCTION_EMAIL', default=False, cast=bool)

if USE_PRODUCTION_EMAIL:
    # Production Email Settings - SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtpout.secureserver.net')  # GoDaddy default
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='orders@joogwear.com')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    EMAIL_TIMEOUT = 30  # Timeout for email sending
    
    # Specific settings for different email providers
    if 'gmail' in EMAIL_HOST:
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
    elif 'secureserver' in EMAIL_HOST:  # GoDaddy
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
        EMAIL_TIMEOUT = 60  # GoDaddy might need longer timeout
else:
    # Development Email Settings - Console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='orders@joogwear.com')
    EMAIL_HOST_PASSWORD = ''

# Default email addresses
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='JOOG Wear <orders@joogwear.com>')
SERVER_EMAIL = config('SERVER_EMAIL', default='JOOG Wear <orders@joogwear.com>')
ADMIN_EMAIL = config('ADMIN_EMAIL', default='orders@joogwear.com')
ADMINS = [('JOOG Admin', ADMIN_EMAIL)]
MANAGERS = ADMINS

# Email settings for order confirmations
ORDER_EMAIL_SUBJECT_PREFIX = '[JOOG] '
ORDER_EMAIL_FROM = config('ORDER_EMAIL_FROM', default='JOOG Wear <orders@joogwear.com>')

# Additional email settings for automation
SEND_ORDER_EMAILS = config('SEND_ORDER_EMAILS', default=True, cast=bool)
RETRY_FAILED_EMAILS = config('RETRY_FAILED_EMAILS', default=True, cast=bool)
EMAIL_RETRY_DELAY_HOURS = config('EMAIL_RETRY_DELAY_HOURS', default=2, cast=int)
MAX_EMAIL_RETRIES = config('MAX_EMAIL_RETRIES', default=3, cast=int)
CLEANUP_EMAIL_ERRORS = config('CLEANUP_EMAIL_ERRORS', default=True, cast=bool)
EMAIL_ERROR_RETENTION_DAYS = config('EMAIL_ERROR_RETENTION_DAYS', default=30, cast=int)

# Company information for emails
SITE_NAME = config('SITE_NAME', default='JOOG Wear')
COMPANY_LOGO_URL = config('COMPANY_LOGO_URL', default='')
COMPANY_ADDRESS = config('COMPANY_ADDRESS', default='# 23/1, Ground Floor, Srinivasa Complex, 2nd Mn. CKC Garden, Mission Road, Bengaluru-560 027')
COMPANY_PHONE = config('COMPANY_PHONE', default='')  # Phone removed from customer emails per requirement
USE_HTTPS = config('USE_HTTPS', default=False, cast=bool)

# Company GST Information
COMPANY_NAME = config('COMPANY_NAME', default='JOOG')
COMPANY_GSTIN = config('COMPANY_GSTIN', default='')
COMPANY_EMAIL = config('COMPANY_EMAIL', default='')
COMPANY_WEBSITE = config('COMPANY_WEBSITE', default='')

# Celery configuration for async email sending (optional)
USE_CELERY_FOR_EMAILS = config('USE_CELERY_FOR_EMAILS', default=False, cast=bool)

if USE_CELERY_FOR_EMAILS:
    # Celery settings
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=False, cast=bool)

# Email configuration logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'email_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'email.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'orders.email_utils': {
            'handlers': ['email_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'invoices.utils': {
            'handlers': ['email_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'orders.signals': {
            'handlers': ['email_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
