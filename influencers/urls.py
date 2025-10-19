from django.urls import path
from . import views
from . import admin_views

app_name = 'influencers'

urlpatterns = [
    # Information and authentication
    path('', views.info_view, name='info'),
    path('info/', views.info_view, name='info'),
    path('access/', views.access_view, name='access'),
    path('login/', views.influencer_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard and main pages
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('orders/', views.orders_view, name='orders'),
    path('profile/', views.profile_view, name='profile'),
    path('monthly-report/', views.monthly_report_view, name='monthly_report'),
    path('monthly-report/export/', views.export_monthly_report_excel, name='export_monthly_report'),
    
    # Admin Management URLs
    path('admin/dashboard/', admin_views.influencer_management_dashboard, name='admin_dashboard'),
    path('admin/list/', admin_views.influencer_list_view, name='admin_list'),
    path('admin/create/', admin_views.influencer_create_view, name='admin_create'),
    path('admin/<int:influencer_id>/', admin_views.influencer_detail_view, name='admin_detail'),
    path('admin/<int:influencer_id>/edit/', admin_views.influencer_edit_view, name='admin_edit'),
    path('admin/<int:influencer_id>/delete/', admin_views.influencer_delete_view, name='admin_delete'),
    path('admin/<int:influencer_id>/coupons/', admin_views.coupon_assignment_view, name='admin_coupon_assignment'),
    path('admin/<int:influencer_id>/assign-coupon/', admin_views.assign_coupon_to_influencer, name='admin_assign_coupon'),
    path('admin/<int:influencer_id>/unassign-coupon/<int:assignment_id>/', admin_views.unassign_coupon_from_influencer, name='admin_unassign_coupon'),
    path('admin/<int:influencer_id>/regenerate-api-key/', admin_views.regenerate_api_key_view, name='admin_regenerate_api_key'),
    path('admin/analytics/', admin_views.influencer_analytics_view, name='admin_analytics'),
    path('admin/export/', admin_views.export_influencers_csv, name='admin_export'),
]
