from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from coupons.models import Coupon
from .forms import OrderForm
import json

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    context = {'cart': cart}
    return render(request, 'orders/cart.html', context)

@login_required
@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_or_create_cart(request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'message': f'{product.name} added to cart!'
        })
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_detail', slug=product.slug)

@login_required
@require_POST
def update_cart_item_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    data = json.loads(request.body)
    quantity = data.get('quantity', 1)
    
    if quantity <= 0:
        cart_item.delete()
        return JsonResponse({'success': True, 'removed': True})
    
    cart_item.quantity = quantity
    cart_item.save()
    
    return JsonResponse({
        'success': True,
        'item_total': float(cart_item.get_total_price()),
        'cart_total': float(cart_item.cart.get_total_price()),
    })

@login_required
@require_POST
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    messages.success(request, 'Item removed from cart!')
    return redirect('orders:cart')

@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('orders:cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.get_total_price()
            order.discount_amount = 0  # Initialize discount amount
            
            # Apply coupon if provided
            coupon_code = request.POST.get('validated_coupon') or request.POST.get('coupon_code')
            
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, active=True)
                    if coupon.is_valid() and order.total_amount >= coupon.minimum_amount:
                        order.coupon = coupon
                        order.discount_amount = coupon.get_discount_amount(order.total_amount)
                        # Note: Don't increment usage here, do it after successful payment
                    else:
                        messages.error(request, 'Coupon is not valid or minimum amount not met!')
                        return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})
                except Coupon.DoesNotExist:
                    messages.error(request, 'Invalid coupon code!')
                    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})
            
            order.final_amount = order.total_amount - order.discount_amount
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear cart
            cart.items.all().delete()
            
            return redirect('orders:payment', order_number=order.order_number)
    else:
        form = OrderForm()
    
    context = {'form': form, 'cart': cart}
    return render(request, 'orders/checkout.html', context)

@login_required
def payment_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if request.method == 'POST':
        # Simulate payment processing
        order.payment_status = 'completed'
        order.status = 'confirmed'
        
        # Increment coupon usage after successful payment
        if order.coupon:
            order.coupon.apply_coupon()
            
        order.save()
        
        messages.success(request, 'Payment successful! Your order has been confirmed.')
        return redirect('orders:order_confirmation', order_number=order.order_number)
    
    context = {'order': order}
    return render(request, 'orders/payment.html', context)

@login_required
def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {'order': order}
    return render(request, 'orders/order_confirmation.html', context)

@staff_member_required
def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {'orders': orders, 'current_status': status}
    return render(request, 'orders/admin_orders.html', context)

@staff_member_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    context = {'order': order}
    return render(request, 'orders/order_detail.html', context)

@staff_member_required
@require_POST
def update_order_status_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}!')
    
    return redirect('orders:order_detail', order_number=order_number)