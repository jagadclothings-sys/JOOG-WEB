from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<str:order_number>/', views.payment_view, name='payment'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    
    # Admin URLs
    path('manage/orders/', views.admin_orders_view, name='admin_orders'),
    path('manage/order/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('manage/update-status/<str:order_number>/', views.update_order_status_view, name='update_order_status'),
]