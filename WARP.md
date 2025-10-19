# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

JOOG is a premium Django e-commerce platform with a red and ivory color scheme. It features a complete e-commerce solution including user authentication, product catalog, shopping cart, order management, and admin dashboard functionality.

### Technology Stack
- **Backend**: Django 5.2.6 with custom user model
- **Frontend**: HTML/CSS with Tailwind CSS styling, vanilla JavaScript
- **Database**: SQLite (development), configurable for PostgreSQL (production)
- **Authentication**: Django Allauth with Google OAuth support
- **Payment**: Stripe integration (partially configured)
- **APIs**: Django REST Framework

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv joog_env
joog_env\Scripts\activate  # Windows
source joog_env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080
```

### Django Management
```bash
# Django shell for data manipulation
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Check for issues
python manage.py check
```

### Testing
The project uses Django's built-in testing framework:
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test products
python manage.py test accounts
python manage.py test orders

# Run with verbose output
python manage.py test --verbosity=2
```

## Architecture Overview

### Project Structure
The project follows Django's app-based architecture:

- **`accounts/`**: Custom user authentication, profiles, Google OAuth
- **`products/`**: Product catalog, categories, reviews, admin dashboard
- **`orders/`**: Shopping cart, order processing, order management
- **`coupons/`**: Discount coupon system
- **`joog_ecommerce/`**: Main project settings, URL configuration, custom admin

### Key Models

**CustomUser** (accounts/models.py): Extended Django user with additional profile fields (phone, address, date_of_birth, etc.)

**Product** (products/models.py): Core product model with category relationship, stock management, and availability tracking

**Order** (orders/models.py): Complete order processing with status tracking, shipping info, and Stripe integration

**Coupon** (coupons/models.py): Flexible discount system supporting percentage and fixed amount coupons

### Admin Interface
The project features a dual admin system:
- **Custom Admin Dashboard**: `/admin-dashboard/` - Custom-styled admin interface with analytics
- **Django Admin**: `/admin/` - Traditional Django admin with custom theming

### URL Structure
```
/                           # Homepage
/products/                  # Product listing
/product/<slug>/            # Product detail
/category/<slug>/           # Category products
/accounts/login/            # Login page
/accounts/register/         # Registration
/accounts/dashboard/        # User dashboard
/orders/cart/              # Shopping cart
/orders/checkout/          # Checkout process
/admin-dashboard/          # Custom admin
/admin/                    # Django admin
```

### Authentication Flow
- Custom user model with extended profile fields
- Django Allauth integration for social login
- Google OAuth configured (requires setup)
- Session-based authentication with custom logout handling

### Payment Integration
- Stripe integration partially configured
- Payment processing in orders app
- Webhook handling setup required for production

## Development Guidelines

### Adding New Features
1. Create models in appropriate app's `models.py`
2. Create forms in `forms.py` if needed
3. Add views to `views.py`
4. Create templates in `templates/<app_name>/`
5. Update URL patterns in `urls.py`
6. Run migrations for model changes

### Database Changes
Always create migrations after model modifications:
```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

### Static Files
- CSS: `static/css/styles.css`
- JavaScript: `static/js/main.js`
- Images: `media/` for uploads, `static/images/` for site assets

### Template System
- Base template: `templates/base.html`
- App-specific templates in `templates/<app_name>/`
- Context processors for categories and cart data

### Custom Management Commands
The project may include custom Django management commands. Run them with:
```bash
python manage.py <command_name>
```

## Configuration

### Environment Variables (Production)
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
```

### Google OAuth Setup
Follow `GOOGLE_OAUTH_SETUP.md` for complete Google Sign-In configuration.

### Stripe Configuration
Update `settings.py` with your Stripe keys and implement webhook handling for production use.

## Important Files

### Core Configuration
- `joog_ecommerce/settings.py`: Main Django settings
- `joog_ecommerce/urls.py`: Root URL configuration
- `requirements.txt`: Python dependencies

### Custom Features
- `joog_ecommerce/admin.py`: Custom admin site configuration
- `accounts/adapters.py`: Custom Allauth adapters
- Context processors in each app for template data

### Static Assets
- `static/css/styles.css`: Main stylesheet with custom color scheme
- `static/js/main.js`: Frontend JavaScript functionality

## Common Tasks

### Add Sample Data
```python
# In Django shell
from products.models import Category, Product
from django.utils.text import slugify

# Create sample categories and products as shown in README.md
```

### User Management
- Admin users: Use Django admin or custom admin dashboard
- Customer management: Available through custom admin interface
- Order tracking: Full order lifecycle management

### Debugging
- Check Django logs in console output
- Use Django Debug Toolbar (install if needed)
- Browser developer tools for frontend issues
- Database queries can be monitored with Django logging

## Security Considerations

- CSRF protection enabled
- User authentication required for sensitive operations
- File upload validation in place
- Admin access restricted to staff users
- Session security configured for production deployment