from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm
from orders.models import Order
from accounts.models import CustomUser
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

def admin_test_view(request):
    """Simple test view to verify admin functionality"""
    return render(request, 'products/admin_test.html', {})

def home_view(request):
    featured_products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()[:6]
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)

def product_list_view(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
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
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

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
    }
    return render(request, 'products/admin_dashboard.html', context)

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
                messages.success(request, f'Product "{product.name}" added successfully!')
                return redirect('products:admin_products')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProductForm()
        
        context = {'form': form}
        return render(request, 'products/add_product.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        form = ProductForm()
        context = {'form': form}
        return render(request, 'products/add_product.html', context)

@staff_member_required
def edit_product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:admin_products')
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product}
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
    """Contact page view"""
    return render(request, 'products/contact.html')

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