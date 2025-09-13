from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-test/', views.admin_test_view, name='admin_test'),
    path('manage/products/', views.admin_products_view, name='admin_products'),
    path('manage/add-product/', views.add_product_view, name='add_product'),
    path('manage/edit-product/<slug:slug>/', views.edit_product_view, name='edit_product'),
    path('manage/delete-product/<slug:slug>/', views.delete_product_view, name='delete_product'),
    path('manage/customers/', views.admin_customers_view, name='admin_customers'),
    path('manage/customer/<int:user_id>/', views.customer_detail_view, name='customer_detail'),
    path('manage/analytics/', views.admin_analytics_view, name='admin_analytics'),
    
    # General Pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('help-center/', views.help_center_view, name='help_center'),
    path('returns/', views.returns_view, name='returns'),
    path('shipping-info/', views.shipping_info_view, name='shipping_info'),
    path('size-guide/', views.size_guide_view, name='size_guide'),
]