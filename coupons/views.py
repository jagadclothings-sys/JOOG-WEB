from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Coupon
from .forms import CouponForm
import json

@staff_member_required
def admin_coupons_view(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    context = {'coupons': coupons}
    return render(request, 'coupons/admin_coupons.html', context)

@staff_member_required
def create_coupon_view(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupons:admin_coupons')
    else:
        form = CouponForm()
    
    context = {'form': form}
    return render(request, 'coupons/create_coupon.html', context)

@staff_member_required
def edit_coupon_view(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupons:admin_coupons')
    else:
        form = CouponForm(instance=coupon)
    
    context = {'form': form, 'coupon': coupon}
    return render(request, 'coupons/edit_coupon.html', context)

@staff_member_required
def delete_coupon_view(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted successfully!')
        return redirect('coupons:admin_coupons')
    
    context = {'coupon': coupon}
    return render(request, 'coupons/delete_coupon.html', context)

def validate_coupon_view(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                code = data.get('code', '').strip()
            else:
                code = request.POST.get('code', '').strip()
        except (json.JSONDecodeError, AttributeError):
            code = request.POST.get('code', '').strip()
            
        if not code:
            return JsonResponse({'valid': False, 'message': 'Please enter a coupon code'})
            
        try:
            coupon = Coupon.objects.get(code=code, active=True)
            if coupon.is_valid():
                # Get cart total for discount calculation
                from orders.models import Cart
                try:
                    cart = Cart.objects.get(user=request.user)
                    cart_total = cart.get_total_price()
                    
                    # Check minimum amount requirement
                    if cart_total < coupon.minimum_amount:
                        return JsonResponse({
                            'valid': False, 
                            'message': f'Minimum order amount of ${coupon.minimum_amount} required'
                        })
                    
                    discount_amount = coupon.get_discount_amount(cart_total)
                    
                    if coupon.discount_type == 'percentage':
                        message = f'Coupon applied! {coupon.discount_value}% off'
                    else:
                        message = f'Coupon applied! ${coupon.discount_value} off'
                        
                except Cart.DoesNotExist:
                    return JsonResponse({'valid': False, 'message': 'Cart not found'})
                
                return JsonResponse({
                    'valid': True,
                    'discount_type': coupon.discount_type,
                    'discount_value': float(coupon.discount_value),
                    'discount_amount': float(discount_amount),
                    'minimum_amount': float(coupon.minimum_amount),
                    'message': message
                })
            else:
                return JsonResponse({'valid': False, 'message': 'Coupon has expired or reached usage limit'})
        except Coupon.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'Invalid coupon code'})
    
    return JsonResponse({'valid': False, 'message': 'Please log in to use coupons'})