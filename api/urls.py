from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'menu-items', views.MenuItemViewSet, basename='menuitem')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'addresses', views.DeliveryAddressViewSet, basename='address')
router.register(r'coupons', views.CouponViewSet, basename='coupon')
router.register(r'advertisements', views.AdvertisementViewSet, basename='advertisement')

urlpatterns = [
    # Authentication
    path('auth/register/', views.register_user, name='api-register'),
    path('auth/login/', views.login_user, name='api-login'),
    path('auth/logout/', views.logout_user, name='api-logout'),
    
    # User Profile
    path('profile/', views.user_profile, name='api-profile'),
    path('profile/update/', views.update_profile, name='api-profile-update'),
    
    # Router URLs
    path('', include(router.urls)),
]
