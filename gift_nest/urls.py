from django.urls import path
from . import views

urlpatterns = [
    # General / Visitor
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/category/<int:category_id>/', views.product_list, name='product_list_by_category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    path('offers/', views.offers_page, name='offers_page'),
    
    # Auth
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Customer
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('cart/', views.cart_page, name='cart_page'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_page, name='checkout_page'),
    path('order-history/', views.order_history, name='order_history'),
    path('track-delivery/<int:order_id>/', views.track_delivery, name='track_delivery'),
    path('profile/', views.profile_page, name='profile_page'),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/return/<int:order_id>/', views.return_order, name='return_order'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('app-admin/products/', views.manage_products, name='manage_products'),
    path('app-admin/categories/', views.manage_categories, name='manage_categories'),
    path('app-admin/stock/', views.manage_stock, name='manage_stock'),
    path('app-admin/orders/', views.manage_orders, name='manage_orders'),
    path('app-admin/customers/', views.manage_customers, name='manage_customers'),
    path('app-admin/delivery/', views.manage_delivery, name='manage_delivery'),
    path('app-admin/reports/', views.reports_page, name='reports_page'),
    
    # Delivery
    path('delivery-dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/assignments/', views.assigned_orders, name='assigned_orders'),
    path('delivery/update-status/<int:assignment_id>/', views.update_delivery_status, name='update_delivery_status'),
]
