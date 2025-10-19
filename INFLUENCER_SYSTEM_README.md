# JOOG Influencer Management System

## Overview
The JOOG Influencer Management System allows you to create influencer accounts, assign coupon codes, and track performance through a dedicated dashboard.

## Features
- ✅ Secure influencer authentication using username and API key
- ✅ Direct dashboard access via shareable links
- ✅ Performance tracking (orders, revenue, commissions)
- ✅ Coupon management and assignment
- ✅ Professional dashboard with statistics
- ✅ Mobile-responsive design
- ✅ Profile management
- ✅ Order tracking and filtering

## How to Create Influencers

### Using Management Command
```bash
# Basic influencer creation
python manage.py create_influencer "Influencer Name" "email@example.com" "username"

# Full influencer creation with social media
python manage.py create_influencer "John Doe" "john@example.com" "johndoe" \
    --phone "+1234567890" \
    --instagram "johndoe_fashion" \
    --youtube "JohnDoeChannel" \
    --commission 7.5

# Create inactive influencer
python manage.py create_influencer "Test User" "test@example.com" "testuser" --inactive
```

### Parameters
- **name**: Full display name of the influencer
- **email**: Email address for contact
- **username**: Unique username for login (required)
- **--phone**: Phone number (optional)
- **--instagram**: Instagram handle without @ (optional)
- **--youtube**: YouTube channel name (optional)
- **--tiktok**: TikTok handle without @ (optional)
- **--website**: Personal website URL (optional)
- **--commission**: Commission rate percentage (default: 0.0)
- **--coupon-codes**: List of coupon codes to assign (optional)
- **--notes**: Admin notes about the influencer (optional)
- **--inactive**: Create the influencer as inactive (optional)

## How Influencers Access Their Dashboard

### Method 1: Direct Link (Recommended)
When you create an influencer, the system generates a direct access link:
```
/influencers/dashboard/?username=johndoe&api_key=API_KEY_HERE
```

Share this link with the influencer for instant access.

### Method 2: Manual Login
Influencers can also log in manually at:
```
/influencers/login/
```

They'll need their:
- Username
- API key (acts as password)

## Dashboard Features

### Main Dashboard (`/influencers/dashboard/`)
- Overview of performance statistics
- Recent orders using their coupons
- Commission earnings
- Quick stats cards
- Coupon performance metrics

### Orders Page (`/influencers/orders/`)
- Complete list of all orders using their coupons
- Filter by order status (pending, confirmed, shipped, delivered, cancelled)
- Filter by specific coupon codes
- Pagination for large datasets
- Order details including customer info and amounts

### Profile Page (`/influencers/profile/`)
- Personal information display
- Social media links
- Commission rate information
- Assigned coupon codes
- API key management
- Quick statistics sidebar

## Security Features
- Secure API key generation using `secrets.token_urlsafe()`
- Session-based authentication
- Protected routes with login decorators
- Scoped data access (influencers only see their own data)
- Secure logout functionality

## Admin Management
Admins can:
1. Create influencer accounts via management command
2. Assign coupon codes through Django admin
3. Monitor influencer performance
4. Update commission rates
5. Activate/deactivate influencers

## Example Workflow

1. **Create Influencer**:
   ```bash
   python manage.py create_influencer "Sarah Fashion" "sarah@fashion.com" "sarahfashion" \
       --instagram "sarah_fashion_guru" \
       --commission 5.0
   ```

2. **Create and Assign Coupon** (via Django admin):
   - Go to Django admin
   - Create new coupon with code "SARAH20" 
   - Set discount to 20%
   - Assign to Sarah's influencer account

3. **Share Access**:
   - Send Sarah the dashboard link from the command output
   - She can immediately access her dashboard

4. **Track Performance**:
   - Sarah logs in to see her stats
   - Views orders using her coupon
   - Tracks commission earnings

## Technical Details

### Models
- **Influencer**: Core influencer data and credentials
- **Integration**: Uses existing Coupon model via foreign key relationship

### Views
- `influencer_login`: Handle authentication
- `dashboard`: Main dashboard with stats
- `orders`: Order listing and filtering
- `profile`: Influencer profile management
- `logout`: Secure logout

### Templates
- `influencers/login.html`: Login form
- `influencers/dashboard.html`: Main dashboard
- `influencers/orders.html`: Order listing
- `influencers/profile.html`: Profile management

### URLs
- `/influencers/login/`: Login page
- `/influencers/dashboard/`: Main dashboard
- `/influencers/orders/`: Order tracking
- `/influencers/profile/`: Profile page
- `/influencers/logout/`: Logout

## Customization

### Commission Calculation
Edit the commission calculation logic in `influencers/views.py`:
```python
commission = (total_revenue * influencer.commission_rate / 100)
```

### Dashboard Metrics
Modify the statistics calculation in the dashboard view to add new metrics or change existing ones.

### Styling
All templates use Tailwind CSS classes. Modify the templates to change the appearance or add new features.

## Testing
You can test the system using the created influencer:
- **Username**: johndoe
- **API Key**: (generated during creation)
- **Direct Link**: Use the dashboard URL from the creation output

## Support
For issues or feature requests, contact the development team or check the Django admin logs for error messages.

---

**Note**: The system is designed to work with your existing Django ecommerce setup and integrates seamlessly with the coupon and order management systems.