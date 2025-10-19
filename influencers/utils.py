import secrets
import string
import logging
from django.db import transaction
from .models import Influencer

logger = logging.getLogger(__name__)

def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_urlsafe(length)

def generate_coupon_code(influencer_name, existing_codes=None):
    """
    Generate a unique coupon code based on influencer name
    
    Args:
        influencer_name (str): The name of the influencer
        existing_codes (list): List of existing coupon codes to avoid duplicates
        
    Returns:
        str: A unique coupon code
    """
    # Sanitize influencer name for coupon code
    name_parts = ''.join(c for c in influencer_name if c.isalnum()).upper()
    prefix = name_parts[:5]
    
    # Add a random alphanumeric suffix
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(chars) for _ in range(3))
    
    code = f"{prefix}{suffix}"
    
    # If code already exists, regenerate with a different suffix
    if existing_codes and code in existing_codes:
        return generate_coupon_code(influencer_name, existing_codes)
    
    return code

@transaction.atomic
def create_influencer(username, name=None, email=None, phone=None, 
                    commission_rate=5.0, bio=None, social_links=None):
    """
    Create a new influencer account with a secure API key
    
    Args:
        username (str): Unique username for the influencer
        name (str): Full name of the influencer
        email (str): Email address
        phone (str): Phone number
        commission_rate (float): Commission percentage
        bio (str): Influencer bio/description
        social_links (dict): Dictionary of social media links
        
    Returns:
        tuple: (Influencer object, API key)
    """
    try:
        if Influencer.objects.filter(username=username).exists():
            raise ValueError(f"Influencer with username '{username}' already exists")
            
        # Generate a secure API key
        api_key = generate_api_key()
        
        # Create influencer object
        influencer = Influencer(
            username=username,
            name=name or '',
            email=email or '',
            phone=phone or '',
            commission_rate=commission_rate,
            api_key=api_key,
            bio=bio or '',
        )
        
        # Add social media links if provided
        if social_links:
            if 'instagram' in social_links:
                influencer.instagram_url = social_links['instagram']
            if 'youtube' in social_links:
                influencer.youtube_url = social_links['youtube']
            if 'tiktok' in social_links:
                influencer.tiktok_url = social_links['tiktok']
            if 'twitter' in social_links:
                influencer.twitter_url = social_links['twitter']
        
        influencer.save()
        logger.info(f"Created new influencer account: {username}")
        
        return influencer, api_key
        
    except Exception as e:
        logger.error(f"Error creating influencer: {str(e)}")
        raise

@transaction.atomic
def regenerate_api_key(username):
    """
    Regenerate API key for an existing influencer
    
    Args:
        username (str): Username of the influencer
        
    Returns:
        str: The new API key
    """
    try:
        influencer = Influencer.objects.get(username=username)
        new_api_key = generate_api_key()
        
        # Store old key for logging
        old_key_prefix = influencer.api_key[:8] if influencer.api_key else "None"
        
        # Update the API key
        influencer.api_key = new_api_key
        influencer.save(update_fields=['api_key'])
        
        logger.info(f"Regenerated API key for influencer: {username} (old key prefix: {old_key_prefix}...)")
        return new_api_key
        
    except Influencer.DoesNotExist:
        raise ValueError(f"No influencer found with username: {username}")
    except Exception as e:
        logger.error(f"Error regenerating API key: {str(e)}")
        raise

def get_dashboard_link(influencer):
    """
    Generate a direct dashboard access link for an influencer
    
    Args:
        influencer (Influencer): The influencer object
        
    Returns:
        str: URL with authentication parameters
    """
    if not influencer or not influencer.api_key:
        return None
        
    return f"/influencers/login/?username={influencer.username}&api_key={influencer.api_key}"

def get_influencer_stats(influencer):
    """
    Get statistics for an influencer
    
    Args:
        influencer (Influencer): The influencer object
        
    Returns:
        dict: Statistics including orders, revenue and commission
    """
    from django.db.models import Sum, Count, Q
    from decimal import Decimal
    
    stats = {
        'total_orders': 0,
        'total_revenue': Decimal('0.00'),
        'total_commission': Decimal('0.00'),
        'active_coupons': 0,
        'order_count_by_month': {},
        'revenue_by_month': {}
    }
    
    # Get all coupons for this influencer
    coupon_ids = influencer.coupons.values_list('id', flat=True)
    if not coupon_ids:
        return stats
    
    # Count active coupons
    stats['active_coupons'] = influencer.coupons.filter(is_active=True).count()
    
    # Get order statistics
    from ecommerce.models import Order
    
    # All orders that used the influencer's coupons
    orders = Order.objects.filter(coupon_id__in=coupon_ids)
    
    stats['total_orders'] = orders.count()
    
    # Calculate revenue and commission
    if stats['total_orders'] > 0:
        revenue_sum = orders.aggregate(
            total=Sum('final_amount')
        ).get('total') or Decimal('0.00')
        
        stats['total_revenue'] = revenue_sum
        stats['total_commission'] = (revenue_sum * influencer.commission_rate / 100).quantize(Decimal('0.01'))
    
    # Get order and revenue by month
    if stats['total_orders'] > 0:
        # This would need to be customized based on your actual Order model
        # The following is a simplified example
        from django.db.models.functions import TruncMonth
        
        by_month = orders.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            revenue=Sum('final_amount')
        ).order_by('month')
        
        for entry in by_month:
            month_key = entry['month'].strftime('%Y-%m')
            stats['order_count_by_month'][month_key] = entry['count']
            stats['revenue_by_month'][month_key] = entry['revenue']
    
    return stats