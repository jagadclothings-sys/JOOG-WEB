from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/', permanent=False), name='accounts_home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('account-details/', views.account_details_view, name='account_details'),
    path('orders/', views.orders_view, name='orders'),
    path('google-login/', views.google_login_view, name='start_google_login'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    # Address management URLs
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address_view, name='edit_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address_view, name='delete_address'),
    path('addresses/set-default/<int:address_id>/', views.set_default_address_view, name='set_default_address'),
    path('addresses/json/<int:address_id>/', views.get_address_json, name='get_address_json'),
    path('addresses/ajax-add/', views.ajax_add_address, name='ajax_add_address'),
    # Invoice URLs
    path('invoices/', views.customer_invoices_view, name='invoices'),
    path('invoices/<str:order_number>/', views.customer_invoice_detail_view, name='invoice_detail'),
    path('invoices/<str:order_number>/download/', views.download_customer_invoice, name='download_invoice'),
    # Admin invoice URLs
    path('admin/invoices/', views.admin_invoices_view, name='admin_invoices'),
    path('admin/invoices/<str:order_number>/', views.admin_invoice_detail_view, name='admin_invoice_detail'),
    path('admin/invoices/<str:order_number>/download/', views.download_admin_invoice, name='download_admin_invoice'),
]
