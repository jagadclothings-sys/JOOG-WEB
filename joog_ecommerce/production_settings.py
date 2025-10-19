import os
from pathlib import Path
from decouple import config, Csv

# Import base settings
from .settings import *

# Production overrides
DEBUG = False

# SECURITY WARNING: Use a secure secret key in production
SECRET_KEY = config('SECRET_KEY', default='django-production-change-this-secret-key-to-something-very-secure-and-random')

# Allowed hosts for production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Static files settings for production
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')

# Email Configuration - Hardcoded (ONLY if you don't want to use .env)
# UNCOMMENT AND UPDATE PASSWORD IF HARDCODING:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtpout.secureserver.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'orders@joogwear.com'
# EMAIL_HOST_PASSWORD = 'YOUR-ACTUAL-EMAIL-PASSWORD-HERE'

# Database for production (keeping SQLite for now, change to PostgreSQL later)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # For PostgreSQL in production:
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': config('DB_NAME'),
        # 'USER': config('DB_USER'),
        # 'PASSWORD': config('DB_PASSWORD'),
        # 'HOST': config('DB_HOST', default='localhost'),
        # 'PORT': config('DB_PORT', default='5432'),
    }
}

# Logging for production
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'email_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'email.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console'],
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
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
    },
}

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com",
]

# Performance optimizations
CONN_MAX_AGE = 60  # Database connection pooling

# Cache configuration (optional - use Redis for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

print("🚀 Production settings loaded successfully!")
print(f"📍 DEBUG mode: {DEBUG}")
print(f"🔒 Allowed hosts: {ALLOWED_HOSTS}")
print(f"📁 Static root: {STATIC_ROOT}")