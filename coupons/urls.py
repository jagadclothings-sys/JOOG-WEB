from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    path('manage/coupons/', views.admin_coupons_view, name='admin_coupons'),
    path('manage/create-coupon/', views.create_coupon_view, name='create_coupon'),
    path('manage/edit-coupon/<int:coupon_id>/', views.edit_coupon_view, name='edit_coupon'),
    path('manage/delete-coupon/<int:coupon_id>/', views.delete_coupon_view, name='delete_coupon'),
    path('validate-coupon/', views.validate_coupon_view, name='validate_coupon'),
]