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
    path('admin-test-email/', views.test_contact_email_reply, name='admin_test_email'),
    path('manage/products/', views.admin_products_view, name='admin_products'),
    path('manage/add-product/', views.add_product_view, name='add_product'),
    path('manage/edit-product/<slug:slug>/', views.edit_product_view, name='edit_product'),
    path('manage/delete-product/<slug:slug>/', views.delete_product_view, name='delete_product'),

    path('manage/categories/', views.admin_categories_view, name='admin_categories'),
    path('manage/add-category/', views.add_category_view, name='add_category'),
    path('manage/edit-category/<slug:slug>/', views.edit_category_view, name='edit_category'),
    path('manage/delete-category/<slug:slug>/', views.delete_category_view, name='delete_category'),
    path('manage/customers/', views.admin_customers_view, name='admin_customers'),
    path('manage/customer/<int:user_id>/', views.customer_detail_view, name='customer_detail'),
    path('manage/analytics/', views.admin_analytics_view, name='admin_analytics'),
    path('manage/reviews/', views.admin_reviews_view, name='admin_reviews'),
    path('reviews/delete/<int:review_id>/', views.delete_review_view, name='delete_review'),
    path('manage/emails/', views.admin_email_management_view, name='admin_email_management'),
    path('manage/contact-requests/', views.admin_contact_requests_view, name='admin_contact_requests'),

    # Banner Management
    path('manage/banners/', views.admin_banners_view, name='admin_banners'),
    path('manage/banners/<int:pk>/move-up/', views.banner_move_up_view, name='banner_move_up'),
    path('manage/banners/<int:pk>/move-down/', views.banner_move_down_view, name='banner_move_down'),
    path('manage/banners/<int:pk>/toggle-active/', views.banner_toggle_active_view, name='banner_toggle_active'),
    path('manage/banners/<int:pk>/delete/', views.banner_delete_view, name='banner_delete'),
    
    # General Pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('help-center/', views.help_center_view, name='help_center'),
    path('returns/', views.returns_view, name='returns'),
    path('shipping-info/', views.shipping_info_view, name='shipping_info'),
    path('size-guide/', views.size_guide_view, name='size_guide'),
]
