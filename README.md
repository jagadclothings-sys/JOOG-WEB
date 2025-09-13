# JOOG E-commerce Platform

A premium Django e-commerce application built with modern design principles and comprehensive functionality.

## Features

### Customer Features
- User registration and authentication
- Product browsing with categories and search
- Shopping cart functionality
- Checkout and payment processing
- Order tracking and history
- Product reviews and ratings
- User dashboard and profile management

### Admin Features
- Comprehensive admin dashboard
- Product management (add, edit, delete)
- Order management and status updates
- Coupon creation and management
- Inventory tracking
- User management

### Design
- Premium red and ivory color scheme
- Responsive design for all devices
- Smooth animations and micro-interactions
- Modern UI with excellent user experience

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv joog_env

# Activate virtual environment
# On Windows:
joog_env\Scripts\activate
# On macOS/Linux:
source joog_env/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 4. Load Sample Data (Optional)

```bash
# Create sample categories and products
python manage.py shell
```

```python
# In Django shell
from products.models import Category, Product
from django.utils.text import slugify

# Create categories
categories = [
    {'name': 'Men\'s Clothing', 'description': 'Premium men\'s fashion'},
    {'name': 'Women\'s Clothing', 'description': 'Elegant women\'s wear'},
    {'name': 'Accessories', 'description': 'Fashion accessories'},
    {'name': 'Footwear', 'description': 'Premium shoes and boots'},
]

for cat_data in categories:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        slug=slugify(cat_data['name']),
        defaults={'description': cat_data['description']}
    )
    print(f"Created category: {category.name}")
```

### 5. Run Development Server

```bash
python manage.py runserver
```

### 6. Access the Application

- Main website: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/
- Admin dashboard: http://127.0.0.1:8000/admin-dashboard/

## Project Structure

```
joog_ecommerce/
├── accounts/                 # User authentication and profiles
├── products/                 # Product catalog and management
├── orders/                   # Shopping cart and order processing
├── coupons/                  # Discount coupons
├── templates/                # HTML templates
├── static/                   # CSS, JS, and static assets
├── media/                    # Uploaded images
├── joog_ecommerce/          # Main project settings
└── requirements.txt          # Python dependencies
```

## Key Models

### User (CustomUser)
- Extended Django user with additional fields
- Phone, address, and other profile information

### Product
- Name, description, price, category
- Stock tracking and availability
- Image uploads

### Order
- Order tracking with status updates
- Shipping information
- Payment processing integration

### Coupon
- Percentage or fixed amount discounts
- Usage limits and expiration dates
- Minimum order requirements

## Admin Features

### Product Management
- Add new products with images
- Edit existing products
- Track inventory levels
- Manage product categories

### Order Management
- View all orders
- Update order status
- Track payments
- Generate order reports

### Coupon Management
- Create discount coupons
- Set usage limits and expiration
- Track coupon usage

## Customization

### Colors
The color scheme can be customized in `static/css/styles.css`:
- Primary red: #DC2626
- Ivory background: #FFF8E7
- Additional color variants as needed

### Styling
- Tailwind CSS for rapid styling
- Custom CSS for brand-specific design
- Responsive breakpoints for all devices

### Payment Integration
Basic Stripe integration is set up. To enable:
1. Get Stripe API keys
2. Update settings.py with your keys
3. Implement webhook handling for production

## Security

- CSRF protection enabled
- User authentication required for sensitive actions
- Admin-only access for management features
- Secure file uploads with validation

## Development Tips

### Adding Sample Products
1. Log into admin panel
2. Create categories first
3. Add products with images
4. Set appropriate stock levels

### Testing Payment Flow
1. Use Stripe test cards
2. Monitor webhooks in Stripe dashboard
3. Test various payment scenarios

### Customizing Templates
- Templates use Django template language
- Responsive design with Tailwind CSS
- Easy to customize colors and layout

## Production Deployment

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

### Static Files
```bash
python manage.py collectstatic
```

### Database
- Use PostgreSQL for production
- Run migrations on production server
- Set up regular database backups

This application provides a solid foundation for a premium e-commerce platform with room for future enhancements and customizations.