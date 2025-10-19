from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    # Admin Management URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/reports/', views.reports_dashboard, name='reports_dashboard'),
    path('admin/list/', views.invoice_list, name='admin_invoice_list'),
    path('admin/generate/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('admin/detail/<int:invoice_id>/', views.invoice_detail, name='admin_invoice_detail'),
    path('admin/pdf/<int:invoice_id>/', views.invoice_pdf, name='admin_invoice_pdf'),
    path('admin/manage-items/<int:invoice_id>/', views.manage_invoice_items, name='manage_invoice_items'),
    path('admin/export/excel/', views.export_invoices_excel, name='export_excel'),
    path('admin/export/orders/', views.export_orders_excel, name='export_orders_excel'),
    path('admin/orders-reports/', views.orders_report_dashboard, name='orders_report_dashboard'),
    path('admin/export/sales-report/', views.export_sales_report_excel, name='export_sales_report_excel'),
    
    # Sales Reports & Analytics
    path('sales-reports/', views.sales_reports_view, name='sales_reports'),
    path('export/sales-report/', views.export_sales_report_excel, name='export_sales_report'),
    path('export/orders-report/', views.export_orders_excel, name='export_orders_report'),
    path('export/invoices/', views.export_invoices_excel, name='export_invoices_excel'),
    
    # Customer URLs
    path('my-invoices/', views.customer_invoices, name='customer_invoices'),
    path('my-invoices/<int:invoice_id>/', views.customer_invoice_detail, name='customer_invoice_detail'),
    path('my-invoices/<int:invoice_id>/download/', views.customer_invoice_pdf, name='customer_invoice_pdf'),
    
    # Legacy URLs (redirect to admin)
    path('', views.admin_dashboard, name='invoice_list'),
    path('detail/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('pdf/<int:invoice_id>/', views.invoice_pdf, name='invoice_pdf'),
]
