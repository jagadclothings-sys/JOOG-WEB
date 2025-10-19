from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CustomPasswordChangeForm, AddressForm
from .models import Wishlist, Address
from orders.models import Order
from products.models import Product

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        """Custom success URL handling for buy now redirects."""
        # Check if there's a buy now intent in session
        if 'buy_now_intent' in self.request.session:
            from django.urls import reverse
            return reverse('orders:process_buy_now')
        
        # Use Django's default success URL behavior
        return super().get_success_url()
    
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    context = {
        'user': request.user,
        'recent_orders': orders,
        'total_orders': Order.objects.filter(user=request.user).count(),
        'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/orders.html', {'orders': orders})

def google_login_view(request):
    """Redirect to Google OAuth login"""
    from django.urls import reverse
    # Use the correct allauth URL pattern for social login
    # The correct URL name for allauth social login is 'socialaccount_login'
    # but without the provider as kwargs, instead provider is part of the URL path
    return redirect('/accounts/google/login/')

@require_http_methods(["GET", "POST"])
def custom_logout_view(request):
    """Custom logout view with user feedback"""
    response = redirect('products:home')
    if request.user.is_authenticated:
        username = request.user.username
        # Fully log out and clear the session
        logout(request)
        request.session.flush()
        # Proactively clear auth/session cookies
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        messages.success(request, f'You have been successfully logged out, {username}!')
    return response

@login_required
def account_details_view(request):
    """Detailed account information view"""
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    total_orders = Order.objects.filter(user=user).count()
    total_spent = Order.objects.filter(user=user, payment_status='completed').aggregate(
        total=models.Sum('final_amount')
    )['total'] or 0
    
    # Get recent activity
    recent_orders = orders[:5]
    
    context = {
        'user': user,
        'orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'account_created': user.date_joined,
        'last_login': user.last_login,
    }
    return render(request, 'accounts/account_details.html', context)

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def wishlist_view(request):
    """View user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
@csrf_exempt
def toggle_wishlist(request):
    """Toggle product in/out of wishlist via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({'error': 'Product ID is required'}, status=400)
            
            product = get_object_or_404(Product, id=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user, 
                product=product
            )
            
            if not created:
                # Item exists, remove it
                wishlist_item.delete()
                return JsonResponse({
                    'status': 'removed',
                    'message': f'{product.name} removed from wishlist'
                })
            else:
                # Item was created, added to wishlist
                return JsonResponse({
                    'status': 'added',
                    'message': f'{product.name} added to wishlist'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@login_required
def remove_from_wishlist(request, product_id):
    """Remove item from wishlist"""
    try:
        wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        messages.success(request, f'{product_name} removed from your wishlist!')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Item not found in your wishlist.')
    
    return redirect('accounts:wishlist')


# Address Management Views
@login_required
def addresses_view(request):
    """View all user addresses"""
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses.html', {'addresses': addresses})


@login_required
def add_address_view(request):
    """Add a new address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:addresses')
    else:
        form = AddressForm()
    return render(request, 'accounts/add_address.html', {'form': form})


@login_required
def edit_address_view(request, address_id):
    """Edit an existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:addresses')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})


@login_required
def delete_address_view(request, address_id):
    """Delete an address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('accounts:addresses')
    
    return render(request, 'accounts/delete_address.html', {'address': address})


@login_required
def set_default_address_view(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Unset all other default addresses for this user
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    messages.success(request, 'Default address updated successfully!')
    return redirect('accounts:addresses')


@login_required
def get_address_json(request, address_id):
    """Get address data as JSON for AJAX requests"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        data = {
            'address_line_1': address.address_line_1,
            'address_line_2': address.address_line_2,
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'country': address.country,
        }
        return JsonResponse(data)
    except Address.DoesNotExist:
        return JsonResponse({'error': 'Address not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def ajax_add_address(request):
    """Add a new address via AJAX from checkout page"""
    try:
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            
            return JsonResponse({
                'success': True,
                'address_id': address.id,
                'address_data': {
                    'id': address.id,
                    'address_type': address.address_type,
                    'address_type_display': address.get_address_type_display(),
                    'address_line_1': address.address_line_1,
                    'address_line_2': address.address_line_2,
                    'city': address.city,
                    'state': address.state,
                    'postal_code': address.postal_code,
                    'country': address.country,
                    'is_default': address.is_default,
                    'full_address': address.get_full_address(),
                },
                'message': 'Address added successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors below.'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding address: {str(e)}'
        }, status=500)


# Invoice Management Views
@login_required
def customer_invoices_view(request):
    """View all customer invoices"""
    orders = Order.objects.filter(
        user=request.user, 
        payment_status='completed'
    ).order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'My Invoices'
    }
    return render(request, 'accounts/customer_invoices.html', context)


@login_required
def customer_invoice_detail_view(request, order_number):
    """View detailed customer invoice"""
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        user=request.user,
        payment_status='completed'
    )
    
    # Calculate GST breakdown - displayed price is inclusive of GST
    # GST rate is 18% (9% CGST + 9% SGST)
    # If final price is inclusive of GST, then:
    # Base price = Final price / 1.18
    # GST amount = Final price - Base price
    
    from decimal import Decimal, ROUND_HALF_UP
    
    gst_rate = Decimal('0.18')  # 18% total GST
    cgst_rate = Decimal('0.09')  # 9% CGST
    sgst_rate = Decimal('0.09')  # 9% SGST
    
    # Calculate base price (without GST) from final amount
    base_amount = order.final_amount / (Decimal('1') + gst_rate)
    total_gst_amount = order.final_amount - base_amount
    cgst_amount = total_gst_amount / Decimal('2')  # Split GST equally between CGST and SGST
    sgst_amount = total_gst_amount / Decimal('2')
    
    # Calculate subtotal and shipping for display
    subtotal = sum(item.get_total_price() for item in order.items.all())
    shipping_cost = Decimal('0')  # Default shipping cost
    if order.final_amount > subtotal:
        shipping_cost = order.final_amount - subtotal
    
    context = {
        'order': order,
        'page_title': f'Invoice #{order.order_number}',
        'base_amount': base_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_gst_amount': total_gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'cgst_amount': cgst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'sgst_amount': sgst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'gst_rate_percent': int(gst_rate * 100),
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
    }
    return render(request, 'accounts/customer_invoice_detail.html', context)


@login_required
def download_customer_invoice(request, order_number):
    """Download customer invoice as PDF"""
    from django.http import HttpResponse
    from django.template.loader import get_template
    import io
    
    try:
        # Try to import WeasyPrint for PDF generation
        from weasyprint import HTML, CSS
        weasyprint_available = True
    except (ImportError, OSError) as e:
        weasyprint_available = False
    
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        user=request.user,
        payment_status='completed'
    )
    
    if weasyprint_available:
        # Generate PDF using WeasyPrint
        template = get_template('accounts/customer_invoice_pdf.html')
        html_content = template.render({'order': order})
        
        # Create PDF
        html = HTML(string=html_content)
        pdf_file = html.write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
        return response
    else:
        # Fallback: Return HTML version
        template = get_template('accounts/customer_invoice_detail.html')
        html_content = template.render({'order': order, 'is_download': True}, request)
        
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.html"'
        return response


@login_required
def admin_invoices_view(request):
    """Admin view for all invoices"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:dashboard')
    
    orders = Order.objects.filter(
        payment_status='completed'
    ).select_related('user').order_by('-created_at')
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            models.Q(order_number__icontains=search_query) |
            models.Q(user__username__icontains=search_query) |
            models.Q(user__email__icontains=search_query)
        )
    
    context = {
        'orders': orders,
        'search_query': search_query,
        'page_title': 'Invoice Management'
    }
    return render(request, 'accounts/admin_invoices.html', context)


@login_required
def admin_invoice_detail_view(request, order_number):
    """Admin detailed invoice view"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:dashboard')
    
    order = get_object_or_404(
        Order, 
        order_number=order_number,
        payment_status='completed'
    )
    
    # Calculate GST breakdown - displayed price is inclusive of GST
    from decimal import Decimal, ROUND_HALF_UP
    
    gst_rate = Decimal('0.18')  # 18% total GST
    base_amount = order.final_amount / (Decimal('1') + gst_rate)
    total_gst_amount = order.final_amount - base_amount
    cgst_amount = total_gst_amount / Decimal('2')
    sgst_amount = total_gst_amount / Decimal('2')
    
    # Calculate subtotal and shipping for display
    subtotal = sum(item.get_total_price() for item in order.items.all())
    shipping_cost = Decimal('0')  # Default shipping cost
    if order.final_amount > subtotal:
        shipping_cost = order.final_amount - subtotal
    
    context = {
        'order': order,
        'page_title': f'Admin Invoice #{order.order_number}',
        'base_amount': base_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_gst_amount': total_gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'cgst_amount': cgst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'sgst_amount': sgst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'gst_rate_percent': int(gst_rate * 100),
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
    }
    return render(request, 'accounts/admin_invoice_detail.html', context)


@login_required
def download_admin_invoice(request, order_number):
    """Download admin invoice as PDF"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:dashboard')
    
    from django.http import HttpResponse
    from django.template.loader import get_template
    
    try:
        # Try to import WeasyPrint for PDF generation
        from weasyprint import HTML, CSS
        weasyprint_available = True
    except (ImportError, OSError) as e:
        weasyprint_available = False
    
    order = get_object_or_404(
        Order, 
        order_number=order_number,
        payment_status='completed'
    )
    
    if weasyprint_available:
        # Generate PDF using WeasyPrint
        template = get_template('accounts/admin_invoice_pdf.html')
        html_content = template.render({'order': order})
        
        # Create PDF
        html = HTML(string=html_content)
        pdf_file = html.write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="admin_invoice_{order.order_number}.pdf"'
        return response
    else:
        # Fallback: Return HTML version
        template = get_template('accounts/admin_invoice_detail.html')
        html_content = template.render({'order': order, 'is_download': True}, request)
        
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="admin_invoice_{order.order_number}.html"'
        return response
