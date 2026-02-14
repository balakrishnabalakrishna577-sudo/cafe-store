from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

urlpatterns = [
    # Home and menu
    path('', views.home_view, name='home'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('menu/item/<slug:slug>/', views.MenuItemDetailView.as_view(), name='menu_item_detail'),
    path('search/', views.search_menu, name='search_menu'),
    
    # Static pages
    path('about/', views.about_view, name='about'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('contact/', views.contact_view, name='contact'),
    
    # Cart functionality
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/toggle-selection/', views.toggle_cart_item_selection, name='toggle_cart_item_selection'),
    
    # Checkout and orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/delete/', views.delete_order, name='delete_order'),
    path('orders/<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Authentication
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(http_method_names=['get', 'post']), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/'
    ), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    

    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Ratings & Reviews
    path('rate-item/', views.rate_item, name='rate_item'),
    path('submit-review/', views.submit_review, name='submit_review'),
    
    # Coupons
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/remove/<int:notification_id>/', views.remove_notification, name='remove_notification'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    
    # Delivery Addresses
    path('addresses/', views.delivery_addresses_view, name='delivery_addresses'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    
    # Order Tracking
    path('track/<str:order_number>/', views.order_tracking_view, name='order_tracking'),
    path('reorder/<str:order_number>/', views.quick_reorder, name='quick_reorder'),
    
    # Recommendations
    path('recommendations/', views.menu_recommendations, name='menu_recommendations'),
    
    # New Features
    path('cart/save-for-later/', views.save_for_later, name='save_for_later'),
    path('cart/move-to-cart/', views.move_to_cart, name='move_to_cart'),
    path('quick-view/<int:item_id>/', views.quick_view_item, name='quick_view_item'),
    path('share-item/<int:item_id>/', views.share_item, name='share_item'),
    path('orders/<str:order_number>/print/', views.print_receipt, name='print_receipt'),
    
    # Custom Admin URLs
    path('custom-admin/', admin_views.admin_login_view, name='admin_login'),
    path('custom-admin/logout/', admin_views.admin_logout_view, name='admin_logout'),
    path('custom-admin/dashboard/', admin_views.admin_dashboard, name='custom_admin_dashboard'),
    path('custom-admin/orders/', admin_views.admin_orders, name='admin_orders'),
    path('custom-admin/orders/<int:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('custom-admin/orders/<int:order_id>/update-status/', admin_views.update_order_status, name='update_order_status'),
    path('custom-admin/orders/<int:order_id>/update-payment-method/', admin_views.update_payment_method, name='update_payment_method'),
    path('custom-admin/orders/<int:order_id>/update-payment-status/', admin_views.update_payment_status, name='update_payment_status'),
    path('custom-admin/orders/<int:order_id>/cancel/', admin_views.admin_cancel_order, name='admin_cancel_order'),
    path('custom-admin/orders/<int:order_id>/mark-payment-received/', admin_views.mark_payment_received, name='mark_payment_received'),
    path('custom-admin/orders/<int:order_id>/mark-received/', admin_views.mark_order_received, name='mark_order_received'),
    path('custom-admin/menu/', admin_views.admin_menu, name='admin_menu'),
    path('custom-admin/menu/add/', admin_views.admin_menu_add, name='admin_menu_add'),
    path('custom-admin/menu/<int:item_id>/edit/', admin_views.admin_menu_edit, name='admin_menu_edit'),
    path('custom-admin/menu/<int:item_id>/delete/', admin_views.admin_menu_delete, name='admin_menu_delete'),
    path('custom-admin/categories/', admin_views.admin_categories, name='admin_categories'),
    path('custom-admin/categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('custom-admin/categories/<int:category_id>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('custom-admin/categories/<int:category_id>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),
    path('custom-admin/customers/', admin_views.admin_customers, name='admin_customers'),
    path('custom-admin/customers/<int:customer_id>/', admin_views.admin_customer_detail, name='admin_customer_detail'),
    path('custom-admin/reviews/', admin_views.admin_reviews, name='admin_reviews'),
    path('custom-admin/reviews/<int:review_id>/delete/', admin_views.admin_delete_review, name='admin_delete_review'),
    path('custom-admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('custom-admin/settings/', admin_views.admin_settings, name='admin_settings'),
    
    # Real-time AJAX endpoints
    path('cart/count/', views.cart_count, name='cart_count'),
    path('cart/add/', views.cart_add_ajax, name='cart_add_ajax'),
    path('cart/auto-save/', views.cart_auto_save, name='cart_auto_save'),
    path('menu/search/', views.menu_search_ajax, name='menu_search_ajax'),
    path('orders/<int:order_id>/status/', views.order_status_ajax, name='order_status_ajax'),
    path('wishlist/toggle/', views.wishlist_toggle_ajax, name='wishlist_toggle_ajax'),
    path('menu/item/<int:item_id>/quick-view/', views.quick_view_ajax, name='quick_view_ajax'),
]