from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .models import Product, Category, Review, ContactRequest, Combo, ProductImage, BannerImage
from .forms import ProductForm, CategoryForm, ReviewForm, ContactForm, ContactReplyForm, ComboForm, ComboItemFormSet, ComboImageFormSet, MultipleImageUploadForm
from orders.models import Order, OrderItem, Cart, CartItem, CartCombo
from orders.email_utils import send_order_confirmation_email, send_admin_order_notification
from accounts.models import CustomUser
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

def send_contact_reply_email(contact_request, subject, message, admin_user):
    """
    Send email reply to customer contact request
    
    Args:
        contact_request: ContactRequest instance
        subject: Email subject
        message: Email message content
        admin_user: User who is sending the reply
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        # Prepare email context
        context = {
            'contact_request': contact_request,
            'message': message,
            'admin_user': admin_user,
            'site_name': getattr(settings, 'SITE_NAME', 'JOOG Wear'),
            'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@joogwear.com'),
            'company_address': '# 23/1, Ground Floor, Srinivasa Complex, 2nd Mn. CKC Garden, Mission Road, Bengaluru-560 027',
            'company_phone': '080 35910158',
        }
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reply from JOOG Wear</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .email-container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 30px; }}
                .message {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background-color: #374151; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                .original-message {{ background-color: #e5e7eb; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>JOOG Wear</h1>
                    <p>Customer Service Reply</p>
                </div>
                
                <div class="content">
                    <h2>Hello {contact_request.first_name},</h2>
                    
                    <div class="message">
                        {message.replace(chr(10), '<br>')}
                    </div>
                    
                    <div class="original-message">
                        <h4>Your Original Message:</h4>
                        <p><strong>Subject:</strong> {contact_request.get_subject_display()}</p>
                        <p><strong>Date:</strong> {contact_request.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Message:</strong><br>{contact_request.message.replace(chr(10), '<br>')}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>JOOG Wear - JAGAD CLOTHINGS</strong></p>
                    <p>{context['company_address']}</p>
                    <p>Phone: {context['company_phone']} | Email: {context['support_email']}</p>
                    <p>Website: <a href="https://www.joogwear.com" style="color: #fbbf24;">www.joogwear.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
Hello {contact_request.first_name},

{message}

---
Your Original Message:
Subject: {contact_request.get_subject_display()}
Date: {contact_request.created_at.strftime('%B %d, %Y at %I:%M %p')}
Message: {contact_request.message}

---
JOOG Wear - JAGAD CLOTHINGS
{context['company_address']}
Phone: {context['company_phone']}
Email: {context['support_email']}
Website: www.joogwear.com
        """
        
        # Email settings
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@joogwear.com')
        to_email = [contact_request.email]
        
        # Create and send email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        msg.send()
        
        return True, "Email sent successfully"
        
    except Exception as e:
        return False, str(e)


def admin_test_view(request):
    """Simple test view to verify admin functionality"""
    return render(request, 'products/admin_test.html', {})

def home_view(request):
    # Handle search queries from home page
    query = request.GET.get('q')
    if query:
        # Redirect to product list with search query
        return redirect(f"/products/?q={query}")
    
    featured_products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()[:6]
    banner_slides = BannerImage.objects.filter(is_active=True).order_by('order', '-created_at')
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'banner_slides': banner_slides,
    }
    return render(request, 'products/home.html', context)

def product_list_view(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        query = query.strip()
        if query:  # Only search if query is not empty after stripping
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
    
    # Category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': query,
    }
    return render(request, 'products/product_list.html', context)

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    reviews = product.reviews.all().order_by('-created_at')
    
    review_form = None
    if request.user.is_authenticated:
        review_form = ReviewForm()
        
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('products:product_detail', slug=slug)
    
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]
    
    # Get available sizes for this product
    available_sizes = product.size_stocks.filter(quantity__gt=0).values('size', 'quantity')
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'related_products': related_products,
        'available_sizes': available_sizes,
    }
    return render(request, 'products/product_detail.html', context)

@require_http_methods(["GET"])
def combo_detail_view(request, slug):
    combo = get_object_or_404(Combo, slug=slug, active=True)
    # Build size options per product
    items = []
    for ci in combo.items.select_related('product').all():
        product = ci.product
        # Gather available sizes for this product
        sizes = list(product.size_stocks.filter(quantity__gt=0).values_list('size', flat=True))
        items.append({
            'product': product,
            'quantity': ci.quantity,
            'sizes': sizes,
        })
    context = {
        'combo': combo,
        'items': items,
    }
    return render(request, 'products/combo_detail.html', context)

@require_http_methods(["POST"])
@login_required
def add_combo_to_cart_view(request, slug):
    combo = get_object_or_404(Combo, slug=slug, active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Expect posted fields like size_<product_id>_<index>
    selections = []
    for ci in combo.items.select_related('product').all():
        product = ci.product
        for idx in range(1, ci.quantity + 1):
            key = f"size_{product.id}_{idx}"
            size = request.POST.get(key)
            if not size:
                messages.error(request, f"Please select size for {product.name} (item {idx}).")
                return redirect('products:combo_detail', slug=slug)
            selections.append((product, size))

    # Validate stock for each size selection
    from products.models import ProductStock
    size_counts = {}
    for product, size in selections:
        size_counts.setdefault((product.id, size), 0)
        size_counts[(product.id, size)] += 1
    for (pid, size), count in size_counts.items():
        ps = ProductStock.objects.filter(product_id=pid, size=size).first()
        if not ps or ps.quantity < count:
            prod = Product.objects.get(id=pid)
            available = ps.quantity if ps else 0
            messages.error(request, f"Only {available} item(s) available for {prod.name} size {size}.")
            return redirect('products:combo_detail', slug=slug)

    # Add items to cart, grouping by a UUID and linking to combo
    group = str(uuid.uuid4())
    original_total = Decimal('0.00')
    for product, size in selections:
        # Add one unit per selection
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': 1, 'combo': combo, 'combo_group': group}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.combo = combo
            cart_item.combo_group = group
            cart_item.save()
        original_total += product.price

    # Compute discount to reach combo price (Option B)
    discount_amount = original_total - combo.price
    if discount_amount < 0:
        discount_amount = Decimal('0.00')  # Do not allow negative discount

    # Record the combo discount for checkout
    CartCombo.objects.create(
        cart=cart,
        combo=combo,
        combo_group=group,
        original_total=original_total,
        combo_price=combo.price,
        discount_amount=discount_amount,
    )

    messages.success(request, f'Combo "{combo.name}" added to cart!')
    return redirect('orders:cart')

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category.html', context)

@staff_member_required
def admin_dashboard_view(request):
    # Get date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Product statistics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=5)
    out_of_stock_products = Product.objects.filter(stock=0)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    recent_orders = Order.objects.filter(created_at__date__gte=last_30_days)
    total_revenue = Order.objects.filter(payment_status='completed').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    monthly_revenue = recent_orders.filter(payment_status='completed').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    
    # Customer statistics
    total_customers = CustomUser.objects.filter(is_staff=False).count()
    new_customers = CustomUser.objects.filter(
        date_joined__date__gte=last_30_days,
        is_staff=False
    ).count()
    
    # Invoice statistics
    from invoices.models import TaxInvoice
    total_invoices = TaxInvoice.objects.count()
    generated_invoices = TaxInvoice.objects.filter(is_generated=True).count()
    pending_invoices = total_invoices - generated_invoices
    invoice_revenue = TaxInvoice.objects.aggregate(total=Sum('final_amount'))['total'] or 0
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__isnull=False).order_by('-total_sold')[:5]
    
    # Recent activity
    recent_orders_list = Order.objects.select_related('user').order_by('-created_at')[:5]
    recent_customers = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'top_products': top_products,
        'recent_orders_list': recent_orders_list,
        'recent_customers': recent_customers,
        'total_invoices': total_invoices,
        'generated_invoices': generated_invoices,
        'pending_invoices': pending_invoices,
        'invoice_revenue': invoice_revenue,
    }
    return render(request, 'products/admin_dashboard.html', context)

@staff_member_required
def admin_combos_view(request):
    combos = Combo.objects.all().order_by('-created_at')
    paginator = Paginator(combos, 20)
    page_number = request.GET.get('page')
    combos = paginator.get_page(page_number)
    return render(request, 'products/admin_combos.html', {'combos': combos})

@staff_member_required
def add_combo_view(request):
    if request.method == 'POST':
        form = ComboForm(request.POST, request.FILES)
        combo_instance = Combo()
        items_formset = ComboItemFormSet(request.POST, instance=combo_instance)
        images_formset = ComboImageFormSet(request.POST, request.FILES, instance=combo_instance)
        if form.is_valid() and items_formset.is_valid() and images_formset.is_valid():
            combo = form.save()
            items_formset.instance = combo
            images_formset.instance = combo
            items_formset.save()
            images_formset.save()
            messages.success(request, f'Combo "{combo.name}" created successfully!')
            return redirect('products:admin_combos')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComboForm()
        combo_instance = Combo()
        items_formset = ComboItemFormSet(instance=combo_instance)
        images_formset = ComboImageFormSet(instance=combo_instance)
    return render(request, 'products/combo_form.html', {
        'form': form,
        'items_formset': items_formset,
        'images_formset': images_formset,
        'action': 'Create'
    })

@staff_member_required
def edit_combo_view(request, slug):
    combo = get_object_or_404(Combo, slug=slug)
    if request.method == 'POST':
        form = ComboForm(request.POST, request.FILES, instance=combo)
        items_formset = ComboItemFormSet(request.POST, instance=combo)
        images_formset = ComboImageFormSet(request.POST, request.FILES, instance=combo)
        if form.is_valid() and items_formset.is_valid() and images_formset.is_valid():
            form.save()
            items_formset.save()
            images_formset.save()
            messages.success(request, 'Combo updated successfully!')
            return redirect('products:admin_combos')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComboForm(instance=combo)
        items_formset = ComboItemFormSet(instance=combo)
        images_formset = ComboImageFormSet(instance=combo)
    return render(request, 'products/combo_form.html', {
        'form': form,
        'items_formset': items_formset,
        'images_formset': images_formset,
        'action': 'Edit',
    })


# =====================
# Banner Management
# =====================
@staff_member_required
def admin_banners_view(request):
    banners = BannerImage.objects.all().order_by('order', '-created_at')
    return render(request, 'products/admin_banners.html', {'banners': banners})


def _swap_banner_order(a: BannerImage, b: BannerImage):
    a.order, b.order = b.order, a.order
    a.save(update_fields=['order'])
    b.save(update_fields=['order'])


@staff_member_required
@require_http_methods(["POST"])
def banner_move_up_view(request, pk):
    banner = get_object_or_404(BannerImage, pk=pk)
    neighbor = (
        BannerImage.objects
        .filter(order__lt=banner.order)
        .order_by('-order', '-created_at')
        .first()
    )
    if neighbor:
        _swap_banner_order(banner, neighbor)
        messages.success(request, f'"{banner.title or f"Banner #{banner.pk}"}" moved up.')
    else:
        # If this is the smallest order, try to decrease order by 1 to keep it first
        if banner.order > 0:
            banner.order = banner.order - 1
            banner.save(update_fields=['order'])
            messages.info(request, 'Adjusted banner order to keep it at the top.')
        else:
            messages.info(request, 'Banner is already at the top.')
    return redirect('products:admin_banners')


@staff_member_required
@require_http_methods(["POST"])
def banner_move_down_view(request, pk):
    banner = get_object_or_404(BannerImage, pk=pk)
    neighbor = (
        BannerImage.objects
        .filter(order__gt=banner.order)
        .order_by('order', 'created_at')
        .first()
    )
    if neighbor:
        _swap_banner_order(banner, neighbor)
        messages.success(request, f'"{banner.title or f"Banner #{banner.pk}"}" moved down.')
    else:
        banner.order = banner.order + 1
        banner.save(update_fields=['order'])
        messages.info(request, 'Adjusted banner order to keep it at the bottom.')
    return redirect('products:admin_banners')


@staff_member_required
@require_http_methods(["POST"])
def banner_toggle_active_view(request, pk):
    banner = get_object_or_404(BannerImage, pk=pk)
    banner.is_active = not banner.is_active
    banner.save(update_fields=['is_active'])
    state = 'activated' if banner.is_active else 'deactivated'
    messages.success(request, f'Banner {state}.')
    return redirect('products:admin_banners')


@staff_member_required
@require_http_methods(["POST"])
def banner_delete_view(request, pk):
    banner = get_object_or_404(BannerImage, pk=pk)
    title = banner.title or f"Banner #{banner.pk}"
    banner.delete()
    messages.success(request, f'"{title}" deleted successfully.')
    return redirect('products:admin_banners')

@staff_member_required
def delete_combo_view(request, slug):
    combo = get_object_or_404(Combo, slug=slug)
    if request.method == 'POST':
        combo.delete()
        messages.success(request, 'Combo deleted successfully!')
        return redirect('products:admin_combos')
    return render(request, 'products/delete_product.html', {'product': combo, 'is_combo': True})

@staff_member_required
def admin_products_view(request):
    products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {'products': products}
    return render(request, 'products/admin_products.html', context)

@staff_member_required
def add_product_view(request):
    try:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save()
                
                # Handle multiple images from drag & drop upload
                multiple_images = request.FILES.getlist('images')
                new_images_count = 0
                
                if multiple_images:
                    # Get alt text data from POST if available
                    alt_texts = request.POST.getlist('image_alt_texts')
                    
                    for index, image_file in enumerate(multiple_images):
                        # Get the alt text for this image (if provided)
                        alt_text = ''
                        if alt_texts and index < len(alt_texts):
                            alt_text = alt_texts[index].strip()
                        
                        # Use default alt text if none provided
                        if not alt_text:
                            alt_text = f"{product.name} - Additional Image"
                        
                        # Create ProductImage instance for each uploaded image
                        ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            alt_text=alt_text
                        )
                        new_images_count += 1
                
                # Handle additional images via traditional formset
                from .forms import ProductImageFormSet
                image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
                if image_formset.is_valid():
                    image_formset.save()
                
                # Success message
                total_additional_images = product.images.count()
                if new_images_count > 0:
                    messages.success(
                        request, 
                        f'Product "{product.name}" added successfully with {new_images_count} additional images from drag & drop! Total additional images: {total_additional_images}'
                    )
                elif total_additional_images > 0:
                    messages.success(
                        request, 
                        f'Product "{product.name}" added successfully with {total_additional_images} additional images!'
                    )
                else:
                    messages.success(request, f'Product "{product.name}" added successfully!')
                
                return redirect('products:admin_products')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProductForm()
            from .forms import ProductImageFormSet
            # Use a temporary unsaved product is not possible; formset requires instance, so handle after save
            image_formset = ProductImageFormSet(instance=Product())
        
        # If we reach here with POST and product exists but images invalid, product remains created; reload formset bound
        if request.method == 'POST' and form.is_valid():
            from .forms import ProductImageFormSet
            image_formset = ProductImageFormSet(request.POST, request.FILES, instance=form.instance)
        
        context = {'form': form, 'image_formset': image_formset}
        return render(request, 'products/add_product.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        form = ProductForm()
        from .forms import ProductImageFormSet
        image_formset = ProductImageFormSet(instance=Product())
        context = {'form': form, 'image_formset': image_formset}
        return render(request, 'products/add_product.html', context)

@staff_member_required
def edit_product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    from .forms import ProductImageFormSet
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save()
            
            # Handle multiple images from drag & drop upload
            multiple_images = request.FILES.getlist('images')
            new_images_count = 0
            
            if multiple_images:
                # Get alt text data from POST if available
                alt_texts = request.POST.getlist('image_alt_texts')
                
                for index, image_file in enumerate(multiple_images):
                    # Get the alt text for this image (if provided)
                    alt_text = ''
                    if alt_texts and index < len(alt_texts):
                        alt_text = alt_texts[index].strip()
                    
                    # Use default alt text if none provided
                    if not alt_text:
                        alt_text = f"{product.name} - Additional Image"
                    
                    # Create ProductImage instance for each uploaded image
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        alt_text=alt_text
                    )
                    new_images_count += 1
            
            # Handle traditional formset images
            if image_formset.is_valid():
                image_formset.save()
            else:
                # If formset has errors but main form is valid, still proceed but show warnings
                if image_formset.errors:
                    messages.warning(request, 'Some existing images could not be updated. Please check the form below.')
            
            # Success message
            total_additional_images = product.images.count()
            if new_images_count > 0:
                messages.success(
                    request, 
                    f'Product updated successfully! Added {new_images_count} new images. Total additional images: {total_additional_images}'
                )
            else:
                messages.success(request, 'Product updated successfully!')
            
            return redirect('products:admin_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
        image_formset = ProductImageFormSet(instance=product)
    
    context = {
        'form': form, 
        'product': product, 
        'image_formset': image_formset,
        'multiple_image_form': MultipleImageUploadForm()
    }
    return render(request, 'products/edit_product.html', context)

@staff_member_required
def delete_product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:admin_products')
    
    context = {'product': product}
    return render(request, 'products/delete_product.html', context)

@staff_member_required
def admin_customers_view(request):
    try:
        customers = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')
        
        # Search functionality
        search_query = request.GET.get('search')
        if search_query:
            customers = customers.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        # Add order statistics for each customer
        for customer in customers:
            try:
                customer.total_orders = customer.orders.count()
                customer.total_spent = customer.orders.filter(
                    payment_status='completed'
                ).aggregate(total=Sum('final_amount'))['total'] or 0
            except Exception as e:
                customer.total_orders = 0
                customer.total_spent = 0
        
        paginator = Paginator(customers, 20)
        page_number = request.GET.get('page')
        customers = paginator.get_page(page_number)
        
        context = {
            'customers': customers,
            'search_query': search_query,
        }
        return render(request, 'products/admin_customers.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred while loading customers: {str(e)}')
        context = {
            'customers': [],
            'search_query': '',
        }
        return render(request, 'products/admin_customers.html', context)

@staff_member_required
def customer_detail_view(request, user_id):
    customer = get_object_or_404(CustomUser, id=user_id, is_staff=False)
    orders = customer.orders.order_by('-created_at')
    
    # Customer statistics
    total_orders = orders.count()
    total_spent = orders.filter(payment_status='completed').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    avg_order_value = orders.filter(payment_status='completed').aggregate(
        avg=Avg('final_amount')
    )['avg'] or 0
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
    }
    return render(request, 'products/customer_detail.html', context)

@staff_member_required
def admin_analytics_view(request):
    try:
        # Date ranges
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        last_90_days = today - timedelta(days=90)
        
        # Revenue analytics
        revenue_7_days = Order.objects.filter(
            created_at__date__gte=last_7_days,
            payment_status='completed'
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        revenue_30_days = Order.objects.filter(
            created_at__date__gte=last_30_days,
            payment_status='completed'
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        revenue_90_days = Order.objects.filter(
            created_at__date__gte=last_90_days,
            payment_status='completed'
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        # Order analytics
        orders_7_days = Order.objects.filter(created_at__date__gte=last_7_days).count()
        orders_30_days = Order.objects.filter(created_at__date__gte=last_30_days).count()
        orders_90_days = Order.objects.filter(created_at__date__gte=last_90_days).count()
        
        # Product analytics
        best_selling_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).filter(total_sold__isnull=False).order_by('-total_sold')[:10]
        
        # Category analytics
        category_sales = Category.objects.annotate(
            total_sold=Sum('products__orderitem__quantity'),
            total_revenue=Sum('products__orderitem__price')
        ).filter(total_sold__isnull=False).order_by('-total_sold')
        
        # Customer analytics
        top_customers = CustomUser.objects.filter(is_staff=False).annotate(
            total_spent=Sum('orders__final_amount'),
            total_orders=Count('orders')
        ).filter(total_spent__isnull=False).order_by('-total_spent')[:10]
        
        context = {
            'revenue_7_days': revenue_7_days,
            'revenue_30_days': revenue_30_days,
            'revenue_90_days': revenue_90_days,
            'orders_7_days': orders_7_days,
            'orders_30_days': orders_30_days,
            'orders_90_days': orders_90_days,
            'best_selling_products': best_selling_products,
            'category_sales': category_sales,
            'top_customers': top_customers,
        }
        return render(request, 'products/admin_analytics.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred while loading analytics: {str(e)}')
        context = {
            'revenue_7_days': 0,
            'revenue_30_days': 0,
            'revenue_90_days': 0,
            'orders_7_days': 0,
            'orders_30_days': 0,
            'orders_90_days': 0,
            'best_selling_products': [],
            'category_sales': [],
            'top_customers': [],
        }
        return render(request, 'products/admin_analytics.html', context)

# General Pages
def about_view(request):
    """About page view"""
    return render(request, 'products/about.html')

def contact_view(request):
    """Contact page view with form handling"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_request = form.save()
            messages.success(
                request, 
                'Thank you for your message! We have received your inquiry and will respond within 24 hours.'
            )
            return redirect('products:contact')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = ContactForm()
    
    context = {
        'form': form
    }
    return render(request, 'products/contact.html', context)

def help_center_view(request):
    """Help Center page view"""
    return render(request, 'products/help_center.html')

def returns_view(request):
    """Returns page view"""
    return render(request, 'products/returns.html')

def shipping_info_view(request):
    """Shipping Info page view"""
    return render(request, 'products/shipping_info.html')

def size_guide_view(request):
    """Size Guide page view"""
    return render(request, 'products/size_guide.html')

# Category Management Views
@staff_member_required
def admin_categories_view(request):
    """Admin view to manage categories"""
    categories = Category.objects.all().order_by('name')
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    
    context = {'categories': categories}
    return render(request, 'products/admin_categories.html', context)

@staff_member_required
def add_category_view(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('products:admin_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'products/add_category.html', context)

@staff_member_required
def edit_category_view(request, slug):
    """Edit existing category"""
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('products:admin_categories')
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form, 'category': category}
    return render(request, 'products/edit_category.html', context)

@staff_member_required
def delete_category_view(request, slug):
    """Delete category"""
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('products:admin_categories')
    
    context = {'category': category}
    return render(request, 'products/delete_category.html', context)


@staff_member_required
def admin_reviews_view(request):
    """Admin view to manage all customer reviews"""
    reviews = Review.objects.select_related('user', 'product').order_by('-created_at')
    
    # Filter by rating if specified
    rating_filter = request.GET.get('rating')
    if rating_filter:
        try:
            rating_filter = int(rating_filter)
            if 1 <= rating_filter <= 5:
                reviews = reviews.filter(rating=rating_filter)
        except ValueError:
            pass
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        reviews = reviews.filter(
            Q(comment__icontains=query) |
            Q(product__name__icontains=query) |
            Q(user__username__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)
    
    # Review statistics
    total_reviews = Review.objects.count()
    rating_stats = {
        'average': Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
        'distribution': {
            5: Review.objects.filter(rating=5).count(),
            4: Review.objects.filter(rating=4).count(),
            3: Review.objects.filter(rating=3).count(),
            2: Review.objects.filter(rating=2).count(),
            1: Review.objects.filter(rating=1).count(),
        }
    }
    
    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'rating_stats': rating_stats,
        'current_rating_filter': rating_filter,
        'search_query': query,
    }
    return render(request, 'products/admin_reviews.html', context)


@staff_member_required
@require_http_methods(["DELETE"])
def delete_review_view(request, review_id):
    """Delete a review (Admin only)"""
    try:
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return JsonResponse({'success': True, 'message': 'Review deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@staff_member_required
def admin_contact_requests_view(request):
    """Admin view to manage contact requests from customers"""
    contact_requests = ContactRequest.objects.all()
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        contact_requests = contact_requests.filter(status=status_filter)
    
    # Filter by subject if specified  
    subject_filter = request.GET.get('subject')
    if subject_filter:
        contact_requests = contact_requests.filter(subject=subject_filter)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        contact_requests = contact_requests.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(message__icontains=query)
        )
    
    # Handle status updates
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        
        if action and request_id:
            try:
                contact_request = ContactRequest.objects.get(id=request_id)
                
                if action.startswith('update_status_'):
                    new_status = action.replace('update_status_', '')
                    if new_status in dict(ContactRequest.STATUS_CHOICES).keys():
                        contact_request.status = new_status
                        contact_request.save()
                        messages.success(request, f'Status updated to {contact_request.get_status_display()}')
                
                elif action == 'add_notes':
                    notes = request.POST.get('admin_notes', '')
                    contact_request.admin_notes = notes
                    contact_request.save()
                    messages.success(request, 'Admin notes updated successfully')
                
                elif action == 'send_reply':
                    # Handle email reply
                    subject = request.POST.get('reply_subject', '')
                    message = request.POST.get('reply_message', '')
                    
                    if subject and message:
                        success, error_msg = send_contact_reply_email(
                            contact_request, subject, message, request.user
                        )
                        
                        if success:
                            # Update status to resolved if it was pending/in_progress
                            if contact_request.status in ['pending', 'in_progress']:
                                contact_request.status = 'resolved'
                            
                            # Add admin note about the reply
                            reply_note = f"Email reply sent on {timezone.now().strftime('%Y-%m-%d %H:%M')}: {subject}"
                            if contact_request.admin_notes:
                                contact_request.admin_notes += f"\n\n{reply_note}"
                            else:
                                contact_request.admin_notes = reply_note
                            
                            contact_request.save()
                            messages.success(request, f'Email reply sent successfully to {contact_request.email}')
                        else:
                            messages.error(request, f'Failed to send email reply: {error_msg}')
                    else:
                        messages.error(request, 'Please provide both subject and message for the reply')
                        
            except ContactRequest.DoesNotExist:
                messages.error(request, 'Contact request not found')
            except Exception as e:
                messages.error(request, f'Error updating contact request: {str(e)}')
    
    # Pagination
    paginator = Paginator(contact_requests, 20)
    page_number = request.GET.get('page')
    contact_requests = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': ContactRequest.objects.count(),
        'pending': ContactRequest.objects.filter(status='pending').count(),
        'in_progress': ContactRequest.objects.filter(status='in_progress').count(),
        'resolved': ContactRequest.objects.filter(status='resolved').count(),
        'closed': ContactRequest.objects.filter(status='closed').count(),
    }
    
    context = {
        'contact_requests': contact_requests,
        'stats': stats,
        'status_choices': ContactRequest.STATUS_CHOICES,
        'subject_choices': ContactRequest.SUBJECT_CHOICES,
        'current_status_filter': status_filter,
        'current_subject_filter': subject_filter,
        'search_query': query,
        'page_title': 'Contact Requests Management',
    }
    return render(request, 'products/admin_contact_requests.html', context)


@staff_member_required
def test_contact_email_reply(request):
    """Test view for contact email reply functionality"""
    if request.method == 'POST':
        # Create a test contact request
        test_contact = ContactRequest(
            first_name="Test",
            last_name="Customer", 
            email="test@example.com",
            subject="general",
            message="This is a test message to verify email functionality."
        )
        
        # Test the email sending function
        success, error_msg = send_contact_reply_email(
            test_contact,
            "Test Email Reply - JOOG Wear",
            "This is a test email reply to verify that the email system is working correctly.",
            request.user
        )
        
        if success:
            messages.success(request, 'Test email sent successfully! Check your email logs or console.')
        else:
            messages.error(request, f'Failed to send test email: {error_msg}')
    
    return render(request, 'products/admin_test.html', {
        'page_title': 'Email Reply Test',
        'test_description': 'Click the button below to test the contact email reply functionality.'
    })


@staff_member_required
def admin_email_management_view(request):
    """Admin view for managing customer emails"""
    orders = Order.objects.select_related('user').order_by('-created_at')[:50]  # Recent orders
    
    # Handle email sending
    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = request.POST.get('order_id')
        
        if action and order_id:
            try:
                order = Order.objects.get(id=order_id)
                
                if action == 'send_confirmation':
                    success = send_order_confirmation_email(order, request)
                    if success:
                        messages.success(request, f'Order confirmation email sent to {order.user.email}')
                    else:
                        messages.error(request, 'Failed to send order confirmation email')
                
                elif action == 'send_admin_notification':
                    success = send_admin_order_notification(order, request)
                    if success:
                        messages.success(request, f'Admin notification email sent')
                    else:
                        messages.error(request, 'Failed to send admin notification email')
                        
            except Order.DoesNotExist:
                messages.error(request, 'Order not found')
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
    
    context = {
        'orders': orders,
        'page_title': 'Email Management',
    }
    return render(request, 'products/admin_email_management.html', context)
