from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from .models import Influencer, InfluencerCoupon
from .forms import InfluencerForm, InfluencerCouponAssignmentForm
from coupons.models import Coupon
from orders.models import Order

@staff_member_required
def influencer_management_dashboard(request):
    """Main dashboard for influencer management"""
    # Get statistics
    total_influencers = Influencer.objects.count()
    active_influencers = Influencer.objects.filter(is_active=True).count()
    inactive_influencers = total_influencers - active_influencers
    
    # Recent influencers
    recent_influencers = Influencer.objects.order_by('-created_at')[:5]
    
    # Get influencer performance data
    influencer_stats = []
    for influencer in recent_influencers:
        assigned_coupons = influencer.coupons.all()
        coupon_codes = [ic.coupon.code for ic in assigned_coupons]
        
        orders = Order.objects.filter(
            coupon__code__in=coupon_codes,
            payment_status='completed'
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        commission = (total_revenue * influencer.commission_rate) / 100
        
        influencer_stats.append({
            'influencer': influencer,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'commission_earned': commission,
            'active_coupons': assigned_coupons.filter(coupon__active=True).count()
        })
    
    # Coupon usage stats
    assigned_coupons = InfluencerCoupon.objects.select_related('coupon', 'influencer').count()
    unassigned_coupons = Coupon.objects.filter(influencers__isnull=True).count()
    
    context = {
        'total_influencers': total_influencers,
        'active_influencers': active_influencers,
        'inactive_influencers': inactive_influencers,
        'influencer_stats': influencer_stats,
        'assigned_coupons': assigned_coupons,
        'unassigned_coupons': unassigned_coupons,
        'recent_influencers': recent_influencers,
    }
    
    return render(request, 'admin/influencer_management/dashboard.html', context)

@staff_member_required
def influencer_list_view(request):
    """List all influencers with filtering and search"""
    influencers = Influencer.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        influencers = influencers.filter(
            Q(name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        influencers = influencers.filter(is_active=True)
    elif status_filter == 'inactive':
        influencers = influencers.filter(is_active=False)
    
    # Order by
    order_by = request.GET.get('order_by', '-created_at')
    influencers = influencers.order_by(order_by)
    
    # Pagination
    paginator = Paginator(influencers, 20)
    page_number = request.GET.get('page')
    influencers_page = paginator.get_page(page_number)
    
    # Get performance data for each influencer
    influencer_data = []
    for influencer in influencers_page:
        assigned_coupons = influencer.coupons.all()
        coupon_codes = [ic.coupon.code for ic in assigned_coupons]
        
        orders = Order.objects.filter(
            coupon__code__in=coupon_codes,
            payment_status='completed'
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        commission = (total_revenue * influencer.commission_rate) / 100
        
        influencer_data.append({
            'influencer': influencer,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'commission_earned': commission,
            'active_coupons': assigned_coupons.filter(coupon__active=True).count(),
            'total_coupons': assigned_coupons.count()
        })
    
    context = {
        'influencer_data': influencer_data,
        'influencers': influencers_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'order_by': order_by,
    }
    
    return render(request, 'admin/influencer_management/list.html', context)

@staff_member_required
def influencer_create_view(request):
    """Create a new influencer"""
    if request.method == 'POST':
        form = InfluencerForm(request.POST)
        if form.is_valid():
            influencer = form.save()
            messages.success(request, f'Influencer "{influencer.name}" created successfully!')
            
            # Redirect to detail view or back to list
            if request.POST.get('save_and_continue'):
                return redirect('influencers:admin_detail', influencer_id=influencer.id)
            else:
                return redirect('influencers:admin_list')
    else:
        form = InfluencerForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'admin/influencer_management/create_edit.html', context)

@staff_member_required
def influencer_detail_view(request, influencer_id):
    """View influencer details"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    
    # Get assigned coupons
    assigned_coupons = influencer.coupons.select_related('coupon')
    coupon_codes = [ic.coupon.code for ic in assigned_coupons]
    
    # Get orders using influencer's coupons
    orders = Order.objects.filter(
        coupon__code__in=coupon_codes
    ).select_related('user', 'coupon').order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    completed_orders = orders.filter(payment_status='completed')
    total_revenue = completed_orders.aggregate(total=Sum('final_amount'))['total'] or 0
    commission_earned = (total_revenue * influencer.commission_rate) / 100
    
    # Recent orders (last 10)
    recent_orders = orders[:10]
    
    # Coupon performance
    coupon_stats = []
    for ic in assigned_coupons:
        coupon_orders = orders.filter(coupon=ic.coupon)
        coupon_revenue = coupon_orders.filter(payment_status='completed').aggregate(total=Sum('final_amount'))['total'] or 0
        coupon_stats.append({
            'assignment': ic,
            'coupon': ic.coupon,
            'orders_count': coupon_orders.count(),
            'revenue': coupon_revenue,
            'commission': (coupon_revenue * influencer.commission_rate) / 100
        })
    
    # Monthly performance (last 6 months)
    monthly_data = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = timezone.now()
        else:
            next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
            month_end = next_month - timedelta(seconds=1)
        
        month_orders = orders.filter(created_at__range=[month_start, month_end])
        month_revenue = month_orders.filter(payment_status='completed').aggregate(total=Sum('final_amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'orders': month_orders.count(),
            'revenue': month_revenue,
            'commission': (month_revenue * influencer.commission_rate) / 100
        })
    
    context = {
        'influencer': influencer,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'commission_earned': commission_earned,
        'recent_orders': recent_orders,
        'coupon_stats': coupon_stats,
        'monthly_data': monthly_data,
        'assigned_coupons_count': assigned_coupons.count(),
        'active_coupons_count': assigned_coupons.filter(coupon__active=True).count(),
    }
    
    return render(request, 'admin/influencer_management/detail.html', context)

@staff_member_required
def influencer_edit_view(request, influencer_id):
    """Edit an existing influencer"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    
    if request.method == 'POST':
        form = InfluencerForm(request.POST, instance=influencer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Influencer "{influencer.name}" updated successfully!')
            
            if request.POST.get('save_and_continue'):
                return redirect('influencers:admin_detail', influencer_id=influencer.id)
            else:
                return redirect('influencers:admin_list')
    else:
        form = InfluencerForm(instance=influencer)
    
    context = {
        'form': form,
        'influencer': influencer,
        'action': 'Edit',
    }
    
    return render(request, 'admin/influencer_management/create_edit.html', context)

@staff_member_required
@require_POST
def influencer_delete_view(request, influencer_id):
    """Delete an influencer"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    
    try:
        influencer_name = influencer.name
        influencer.delete()
        messages.success(request, f'Influencer "{influencer_name}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting influencer: {str(e)}')
    
    return redirect('influencers:admin_list')

@staff_member_required
def coupon_assignment_view(request, influencer_id):
    """Manage coupon assignments for an influencer"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    
    # Get assigned and unassigned coupons
    assigned_coupons = influencer.coupons.select_related('coupon')
    assigned_coupon_ids = [ic.coupon.id for ic in assigned_coupons]
    unassigned_coupons = Coupon.objects.filter(~Q(id__in=assigned_coupon_ids))
    
    context = {
        'influencer': influencer,
        'assigned_coupons': assigned_coupons,
        'unassigned_coupons': unassigned_coupons,
    }
    
    return render(request, 'admin/influencer_management/coupon_assignment.html', context)

@staff_member_required
@require_POST
def assign_coupon_to_influencer(request, influencer_id):
    """Assign a coupon to an influencer"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    
    coupon_id = request.POST.get('coupon_id')
    notes = request.POST.get('notes', '')
    
    if not coupon_id:
        messages.error(request, 'Please select a coupon to assign.')
        return redirect('influencers:admin_coupon_assignment', influencer_id=influencer_id)
    
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        
        # Check if already assigned
        if InfluencerCoupon.objects.filter(influencer=influencer, coupon=coupon).exists():
            messages.error(request, f'Coupon "{coupon.code}" is already assigned to this influencer.')
        else:
            # Create assignment
            assignment = InfluencerCoupon.objects.create(
                influencer=influencer,
                coupon=coupon,
                assigned_by=request.user,
                notes=notes
            )
            messages.success(request, f'Coupon "{coupon.code}" assigned to "{influencer.name}" successfully!')
    
    except Coupon.DoesNotExist:
        messages.error(request, 'Selected coupon does not exist.')
    except Exception as e:
        messages.error(request, f'Error assigning coupon: {str(e)}')
    
    return redirect('influencers:admin_coupon_assignment', influencer_id=influencer_id)

@staff_member_required
@require_POST
def unassign_coupon_from_influencer(request, influencer_id, assignment_id):
    """Unassign a coupon from an influencer"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    assignment = get_object_or_404(InfluencerCoupon, id=assignment_id, influencer=influencer)
    
    try:
        coupon_code = assignment.coupon.code
        assignment.delete()
        messages.success(request, f'Coupon "{coupon_code}" unassigned from "{influencer.name}" successfully!')
    except Exception as e:
        messages.error(request, f'Error unassigning coupon: {str(e)}')
    
    return redirect('influencers:admin_coupon_assignment', influencer_id=influencer_id)

@staff_member_required
def influencer_analytics_view(request):
    """Analytics dashboard for influencers"""
    # Overall statistics
    total_influencers = Influencer.objects.count()
    active_influencers = Influencer.objects.filter(is_active=True).count()
    
    # Performance data
    influencer_performance = []
    for influencer in Influencer.objects.filter(is_active=True):
        assigned_coupons = influencer.coupons.all()
        coupon_codes = [ic.coupon.code for ic in assigned_coupons]
        
        orders = Order.objects.filter(
            coupon__code__in=coupon_codes,
            payment_status='completed'
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        commission = (total_revenue * influencer.commission_rate) / 100
        
        if total_orders > 0:  # Only include influencers with orders
            influencer_performance.append({
                'influencer': influencer,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'commission_earned': commission,
                'avg_order_value': total_revenue / total_orders if total_orders > 0 else 0
            })
    
    # Sort by revenue
    influencer_performance.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    # Monthly trends
    monthly_trends = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i == 0:
            month_end = timezone.now()
        else:
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end = next_month - timedelta(seconds=1)
        
        # Get all influencer orders for this month
        all_coupon_codes = []
        for inf in Influencer.objects.filter(is_active=True):
            all_coupon_codes.extend([ic.coupon.code for ic in inf.coupons.all()])
        
        month_orders = Order.objects.filter(
            coupon__code__in=all_coupon_codes,
            payment_status='completed',
            created_at__range=[month_start, month_end]
        )
        
        month_revenue = month_orders.aggregate(total=Sum('final_amount'))['total'] or 0
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'orders': month_orders.count(),
            'revenue': month_revenue
        })
    
    monthly_trends.reverse()  # Show oldest to newest
    
    context = {
        'total_influencers': total_influencers,
        'active_influencers': active_influencers,
        'influencer_performance': influencer_performance[:10],  # Top 10
        'monthly_trends': monthly_trends,
    }
    
    return render(request, 'admin/influencer_management/analytics.html', context)

@staff_member_required
def export_influencers_csv(request):
    """Export influencers data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="influencers_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Username', 'Email', 'Phone', 'Commission Rate',
        'Status', 'Total Orders', 'Total Revenue', 'Commission Earned',
        'Active Coupons', 'Created Date'
    ])
    
    for influencer in Influencer.objects.all():
        assigned_coupons = influencer.coupons.all()
        coupon_codes = [ic.coupon.code for ic in assigned_coupons]
        
        orders = Order.objects.filter(
            coupon__code__in=coupon_codes,
            payment_status='completed'
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        commission = (total_revenue * influencer.commission_rate) / 100
        active_coupons = assigned_coupons.filter(coupon__active=True).count()
        
        writer.writerow([
            influencer.id,
            influencer.name,
            influencer.username,
            influencer.email,
            influencer.phone,
            f"{influencer.commission_rate}%",
            "Active" if influencer.is_active else "Inactive",
            total_orders,
            f"₹{total_revenue:.2f}",
            f"₹{commission:.2f}",
            active_coupons,
            influencer.created_at.strftime('%Y-%m-%d')
        ])
    
    return response

@staff_member_required
@require_POST
def regenerate_api_key_view(request, influencer_id):
    """Regenerate API key for an influencer"""
    influencer = get_object_or_404(Influencer, id=influencer_id)
    
    try:
        new_api_key = influencer.regenerate_api_key()
        messages.success(request, f'API key regenerated successfully for "{influencer.name}"')
        
        # Return new key in JSON if AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'new_api_key': new_api_key,
                'message': 'API key regenerated successfully!'
            })
    
    except Exception as e:
        messages.error(request, f'Error regenerating API key: {str(e)}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return redirect('influencers:admin_detail', influencer_id=influencer_id)