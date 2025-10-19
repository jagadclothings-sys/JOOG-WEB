from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product, ProductStock
from coupons.models import Coupon
from accounts.models import Address
from .forms import OrderForm
from .email_utils import send_order_confirmation_email, send_admin_order_notification, send_order_status_update_email
import json

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def process_buy_now_view(request):
    """Process buy now intent after user logs in."""
    buy_now_intent = request.session.get('buy_now_intent')
    
    if not buy_now_intent:
        messages.error(request, 'No purchase intent found. Please try again.')
        return redirect('products:home')
    
    # Extract product details from session
    product_id = buy_now_intent['product_id']
    size = buy_now_intent['size']
    quantity = buy_now_intent['quantity']
    
    # Clear the intent from session
    del request.session['buy_now_intent']
    
    # Get the product and validate it's still available
    try:
        product = get_object_or_404(Product, id=product_id, available=True)
    except:
        messages.error(request, 'The product you were trying to purchase is no longer available.')
        return redirect('products:home')
    
    cart = get_or_create_cart(request.user)

    # Check size-specific stock availability
    try:
        product_stock = ProductStock.objects.get(product=product, size=size)
        available_stock = product_stock.quantity
    except ProductStock.DoesNotExist:
        messages.error(request, f'Size {size} is not available for this product!')
        return redirect('products:product_detail', slug=product.slug)

    if available_stock < quantity:
        messages.error(request, f'Only {available_stock} items available in size {size}!')
        return redirect('products:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > available_stock:
            messages.error(request, f'Only {available_stock} items available in size {size}! You already have {cart_item.quantity} in your cart.')
            return redirect('products:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()

    messages.success(request, f'{product.name} added to your cart!')
    # Go straight to checkout
    return redirect('orders:checkout')

@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    context = {'cart': cart}
    return render(request, 'orders/cart.html', context)

@login_required
@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    size = request.POST.get('size', 'M')
    cart = get_or_create_cart(request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check size-specific stock availability
    try:
        product_stock = ProductStock.objects.get(product=product, size=size)
        available_stock = product_stock.quantity
    except ProductStock.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Size {size} is not available for this product!'
            })
        messages.error(request, f'Size {size} is not available for this product!')
        return redirect('products:product_detail', slug=product.slug)
    
    if available_stock < quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Only {available_stock} items available in size {size}!'
            })
        messages.error(request, f'Only {available_stock} items available in size {size}!')
        return redirect('products:product_detail', slug=product.slug)
    
    print('Size chosen:', size)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        # Check if total quantity exceeds size-specific stock
        if new_quantity > available_stock:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Only {available_stock} items available in size {size}! You already have {cart_item.quantity} in your cart.'
                })
            messages.error(request, f'Only {available_stock} items available in size {size}! You already have {cart_item.quantity} in your cart.')
            return redirect('products:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'message': f'{product.name} added to cart!'
        })
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_detail', slug=product.slug)

@require_POST
def buy_now_view(request, product_id):
    """Add the selected product to cart and go directly to checkout.
    If user is not logged in, store the purchase intent and redirect to login.
    """
    product = get_object_or_404(Product, id=product_id, available=True)
    size = request.POST.get('size', 'M')
    quantity = int(request.POST.get('quantity', 1))
    
    # If user is not authenticated, store purchase intent and redirect to login
    if not request.user.is_authenticated:
        request.session['buy_now_intent'] = {
            'product_id': product_id,
            'size': size,
            'quantity': quantity
        }
        from django.urls import reverse
        login_url = reverse('accounts:login')
        return redirect(f'{login_url}?next={reverse("orders:process_buy_now")}')
    
    # User is authenticated, process normally
    cart = get_or_create_cart(request.user)

    # Check size-specific stock availability
    try:
        product_stock = ProductStock.objects.get(product=product, size=size)
        available_stock = product_stock.quantity
    except ProductStock.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Size {size} is not available for this product!'
            })
        messages.error(request, f'Size {size} is not available for this product!')
        return redirect('products:product_detail', slug=product.slug)

    if available_stock < quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Only {available_stock} items available in size {size}!'
            })
        messages.error(request, f'Only {available_stock} items available in size {size}!')
        return redirect('products:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > available_stock:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Only {available_stock} items available in size {size}! You already have {cart_item.quantity} in your cart.'
                })
            messages.error(request, f'Only {available_stock} items available in size {size}! You already have {cart_item.quantity} in your cart.')
            return redirect('products:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()

    # Go straight to checkout
    return redirect('orders:checkout')

@login_required
@require_POST
def update_cart_item_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    data = json.loads(request.body)
    quantity = data.get('quantity', 1)
    
    if quantity <= 0:
        cart_item.delete()
        return JsonResponse({'success': True, 'removed': True})
    
    # Check size-specific stock availability
    try:
        product_stock = ProductStock.objects.get(product=cart_item.product, size=cart_item.size)
        available_stock = product_stock.quantity
    except ProductStock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'Size {cart_item.size} is not available for this product!'
        })
    
    if quantity > available_stock:
        return JsonResponse({
            'success': False,
            'message': f'Only {available_stock} items available in size {cart_item.size}!'
        })
    
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
    
    # Validate size-specific stock availability before checkout
    for cart_item in cart.items.all():
        try:
            product_stock = ProductStock.objects.get(product=cart_item.product, size=cart_item.size)
            available_stock = product_stock.quantity
        except ProductStock.DoesNotExist:
            messages.error(request, f'Size {cart_item.size} is no longer available for {cart_item.product.name}! Please update your cart.')
            return redirect('orders:cart')
            
        if cart_item.quantity > available_stock:
            messages.error(request, f'Only {available_stock} items of {cart_item.product.name} (size {cart_item.size}) available in stock! Please update your cart.')
            return redirect('orders:cart')
    
    # Get user's addresses
    user = request.user
    user_addresses = Address.objects.filter(user=user)
    default_address = user_addresses.filter(is_default=True).first()
    
    # Determine if user has a saved address (legacy support)
    saved_address = getattr(user, 'address', '')
    saved_city = getattr(user, 'city', '')
    saved_state = getattr(user, 'state', '')
    saved_postal = getattr(user, 'postal_code', '')
    saved_country = getattr(user, 'country', '')
    has_legacy_address = bool(saved_address and saved_city and saved_postal and saved_country)

    if request.method == 'POST':
        form = OrderForm(request.POST, user=user)
        
        # Handle address selection
        selected_address_id = request.POST.get('selected_address')
        use_saved = request.POST.get('use_saved') == '1'
        
        if selected_address_id:
            try:
                selected_address = Address.objects.get(id=selected_address_id, user=user)
                # Fill form data with selected address
                data = request.POST.copy()
                data['shipping_address'] = selected_address.address_line_1
                if selected_address.address_line_2:
                    data['shipping_address'] += ', ' + selected_address.address_line_2
                data['shipping_city'] = selected_address.city
                data['shipping_state'] = selected_address.state
                data['shipping_postal_code'] = selected_address.postal_code
                data['shipping_country'] = selected_address.country
                form = OrderForm(data, user=user)
            except Address.DoesNotExist:
                form = OrderForm(request.POST, user=user)
        elif use_saved and has_legacy_address:
            data = request.POST.copy()
            data['shipping_address'] = saved_address
            data['shipping_city'] = saved_city
            data['shipping_state'] = saved_state
            data['shipping_postal_code'] = saved_postal
            data['shipping_country'] = saved_country
            form = OrderForm(data, user=user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            # Calculate base totals from cart
            order.total_amount = cart.get_total_price()
            # Initialize discount with combo discounts (Option B)
            from decimal import Decimal
            combo_discounts_total = sum((cc.discount_amount for cc in cart.combos.all()), Decimal('0.00'))
            order.discount_amount = combo_discounts_total
            
            # Save selected address reference if provided
            selected_address_id = request.POST.get('selected_address')
            if selected_address_id:
                try:
                    order.selected_address = Address.objects.get(id=selected_address_id, user=user)
                except Address.DoesNotExist:
                    pass
            
            # Apply coupon if provided
            coupon_code = request.POST.get('validated_coupon') or request.POST.get('coupon_code')
            
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, active=True)
                    if coupon.is_valid() and order.total_amount >= coupon.minimum_amount:
                        order.coupon = coupon
                        # Add coupon discount in addition to combo discount
                        order.discount_amount = order.discount_amount + coupon.get_discount_amount(order.total_amount)
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
                    size=cart_item.size,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear cart (items and combo records)
            cart.items.all().delete()
            cart.combos.all().delete()
            
            return redirect('orders:payment', order_number=order.order_number)
    else:
        initial = {}
        # Pre-fill with default address if available
        if default_address:
            initial = {
                'shipping_address': default_address.address_line_1 + (', ' + default_address.address_line_2 if default_address.address_line_2 else ''),
                'shipping_city': default_address.city,
                'shipping_state': default_address.state,
                'shipping_postal_code': default_address.postal_code,
                'shipping_country': default_address.country,
            }
        elif has_legacy_address:
            initial = {
                'shipping_address': saved_address,
                'shipping_city': saved_city,
                'shipping_state': saved_state,
                'shipping_postal_code': saved_postal,
                'shipping_country': saved_country,
            }
        form = OrderForm(initial=initial, user=user)
    
    context = {
        'form': form, 
        'cart': cart, 
        'user_addresses': user_addresses,
        'default_address': default_address,
        'has_legacy_address': has_legacy_address, 
        'legacy_address': {
            'address': saved_address,
            'city': saved_city,
            'state': saved_state,
            'postal': saved_postal,
            'country': saved_country,
        }
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def payment_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    # Show payment page with PhonePe button
    context = {'order': order}
    return render(request, 'orders/payment.html', context)


def _finalize_order_success(order, request):
    """Common order success flow: reduce stock, update statuses, send emails."""
    # Reduce size-specific stock for each item in the order
    for order_item in order.items.all():
        try:
            product_stock = ProductStock.objects.get(product=order_item.product, size=order_item.size)
            product_stock.quantity -= order_item.quantity
            if product_stock.quantity < 0:
                product_stock.quantity = 0
            product_stock.save()

            # Update aggregate stock for legacy compatibility
            order_item.product.stock = order_item.product.total_stock()

            # Mark product as unavailable if no sizes are in stock
            if order_item.product.total_stock() <= 0:
                order_item.product.available = False

            order_item.product.save()
        except ProductStock.DoesNotExist:
            messages.error(request, f'Error reducing stock for {order_item.product.name} (size {order_item.size}). Please contact support.')
            continue

    # Increment coupon usage after successful payment
    if order.coupon:
        order.coupon.apply_coupon()

    order.save()

    # Send order confirmation email to customer
    send_order_confirmation_email(order, request)

    # Send order notification email to admin
    send_admin_order_notification(order, request)


@login_required
def phonepe_initiate(request, order_number):
    """Initiate PhonePe payment and redirect user to PhonePe checkout."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Validate stock one last time before redirecting to payment
    for order_item in order.items.all():
        try:
            product_stock = ProductStock.objects.get(product=order_item.product, size=order_item.size)
            available_stock = product_stock.quantity
        except ProductStock.DoesNotExist:
            messages.error(request, f'Size {order_item.size} is no longer available for {order_item.product.name}! Please update your cart.')
            return redirect('orders:cart')
        if order_item.quantity > available_stock:
            messages.error(request, f'Only {available_stock} items of {order_item.product.name} (size {order_item.size}) available in stock! Please update your cart.')
            return redirect('orders:cart')

    # TEMPORARY: Direct to order confirmation for testing
    # TODO: Remove this when PhonePe sandbox is properly configured
    
    # Check if we're in development/testing mode
    from django.conf import settings
    if getattr(settings, 'DEBUG', False) or getattr(settings, 'PHONEPE_ENV', 'SANDBOX') == 'SANDBOX':
        # Simulate successful payment for testing
        order.phonepe_merchant_txn_id = order.order_number
        order.phonepe_txn_id = f"TEST_TXN_{order.order_number}"
        order.payment_status = 'completed'
        order.status = 'confirmed'
        order.save()
        
        # Finalize order (reduce stock, send emails, etc.)
        _finalize_order_success(order, request)
        
        messages.success(request, 'Payment successful! Your order has been confirmed. (Test Mode)')
        return redirect('orders:order_confirmation', order_number=order.order_number)
    
    # Production PhonePe Integration (when ready)
    # Assign merchant txn id if not set (use order number by default)
    if not order.phonepe_merchant_txn_id:
        order.phonepe_merchant_txn_id = order.order_number
        order.save(update_fields=['phonepe_merchant_txn_id'])

    from payments.phonepe import initiate_payment
    try:
        resp = initiate_payment(order, request)
    except Exception as e:
        messages.error(request, f'Failed to initiate payment: {e}')
        return redirect('orders:payment', order_number=order.order_number)

    # PhonePe success response contains instrumentResponse.redirectInfo.url
    redirect_url = None
    if isinstance(resp, dict) and resp.get('success') and resp.get('data'):
        data = resp['data']
        # Save raw response for auditing
        order.phonepe_meta = resp
        order.save(update_fields=['phonepe_meta'])
        instr = data.get('instrumentResponse') or {}
        redirect_info = instr.get('redirectInfo') or {}
        redirect_url = redirect_info.get('url')

    if not redirect_url:
        messages.error(request, 'PhonePe did not return a redirect URL. Please try again later.')
        return redirect('orders:payment', order_number=order.order_number)

    return redirect(redirect_url)


@login_required
def phonepe_callback(request):
    """Handle PhonePe redirect/callback, verify status, and finalize order."""
    # Accept both GET/POST parameters
    merchant_txn_id = request.POST.get('merchantTransactionId') or request.GET.get('merchantTransactionId')
    if not merchant_txn_id:
        messages.error(request, 'Invalid payment callback: missing transaction id.')
        return redirect('products:home')

    order = get_object_or_404(Order, phonepe_merchant_txn_id=merchant_txn_id, user=request.user)

    from payments.phonepe import status_check
    try:
        status_resp = status_check(merchant_txn_id)
    except Exception as e:
        messages.error(request, f'Failed to verify payment: {e}')
        return redirect('orders:payment', order_number=order.order_number)

    # Interpret status response
    success = False
    txn_id = None
    if isinstance(status_resp, dict) and status_resp.get('success'):
        code = status_resp.get('code')
        data = status_resp.get('data') or {}
        state = (data.get('state') or data.get('paymentState') or '').upper()
        txn_id = data.get('transactionId') or data.get('providerReferenceId')
        # Consider success when code indicates success or state is completed/success
        success = (code in ('PAYMENT_SUCCESS', 'SUCCESS')) or (state in ('COMPLETED', 'SUCCESS'))

    # Persist meta info regardless
    order.phonepe_meta = status_resp
    if txn_id:
        order.phonepe_txn_id = txn_id

    if success:
        order.payment_status = 'completed'
        order.status = 'confirmed'
        order.save(update_fields=['payment_status', 'status', 'phonepe_txn_id', 'phonepe_meta'])
        _finalize_order_success(order, request)
        messages.success(request, 'Payment successful! Your order has been confirmed.')
        return redirect('orders:order_confirmation', order_number=order.order_number)
    else:
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status', 'phonepe_meta'])
        messages.error(request, 'Payment failed or was not completed. You can try again.')
        return redirect('orders:payment', order_number=order.order_number)

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
    old_status = order.status
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        
        # Send status update email to customer
        send_order_status_update_email(order, old_status, new_status, request)
        
        messages.success(request, f'Order status updated to {order.get_status_display()}! Customer has been notified via email.')
    
    return redirect('orders:order_detail', order_number=order_number)

@login_required
def customer_order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {'order': order}
    return render(request, 'orders/customer_order_detail.html', context)