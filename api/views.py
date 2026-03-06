from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from decimal import Decimal

from cafe.models import (
    Category, MenuItem, UserProfile, Cart, Order, OrderItem,
    Review, Wishlist, Rating, Coupon, Notification,
    DeliveryAddress, OrderTracking, Advertisement
)
from .serializers import (
    CategorySerializer, MenuItemSerializer, UserProfileSerializer,
    CartItemSerializer, OrderSerializer, ReviewSerializer,
    WishlistSerializer, RatingSerializer, CouponSerializer,
    NotificationSerializer, DeliveryAddressSerializer,
    OrderTrackingSerializer, AdvertisementSerializer,
    UserRegistrationSerializer, UserSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by deleting token"""
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for menu items"""
    queryset = MenuItem.objects.filter(available=True)
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['price', 'created_at', 'name']
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by item type
        item_type = self.request.query_params.get('item_type')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        # Filter featured items
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_to_cart(self, request, slug=None):
        """Add item to cart"""
        menu_item = self.get_object()
        quantity = int(request.data.get('quantity', 1))
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menu_item=menu_item,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({
            'message': 'Item added to cart',
            'cart_item': CartItemSerializer(cart_item).data
        })


class CartViewSet(viewsets.ModelViewSet):
    """API endpoint for cart"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, saved_for_later=False)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get cart summary"""
        cart_items = self.get_queryset().filter(is_selected=True)
        cart_total = sum(item.get_total_price() for item in cart_items)
        delivery_fee = Decimal('5.00') if cart_total > 0 else Decimal('0.00')
        grand_total = cart_total + delivery_fee
        
        return Response({
            'items_count': cart_items.count(),
            'cart_total': float(cart_total),
            'delivery_fee': float(delivery_fee),
            'grand_total': float(grand_total)
        })
    
    @action(detail=True, methods=['post'])
    def toggle_selection(self, request, pk=None):
        """Toggle cart item selection"""
        cart_item = self.get_object()
        cart_item.is_selected = not cart_item.is_selected
        cart_item.save()
        return Response({'is_selected': cart_item.is_selected})
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear cart"""
        self.get_queryset().delete()
        return Response({'message': 'Cart cleared'})


class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint for orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get order tracking updates"""
        order = self.get_object()
        tracking = OrderTracking.objects.filter(order=order).order_by('-created_at')
        serializer = OrderTrackingSerializer(tracking, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'Order cancelled successfully'})
        return Response({
            'error': 'Order cannot be cancelled'
        }, status=status.HTTP_400_BAD_REQUEST)


class WishlistViewSet(viewsets.ModelViewSet):
    """API endpoint for wishlist"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        menu_item_id = self.request.query_params.get('menu_item')
        if menu_item_id:
            return Review.objects.filter(menu_item_id=menu_item_id)
        return Review.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read'})


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """API endpoint for delivery addresses"""
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set address as default"""
        address = self.get_object()
        DeliveryAddress.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'message': 'Default address updated'})


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for coupons"""
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Coupon.objects.filter(is_active=True)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def validate(self, request):
        """Validate coupon code"""
        code = request.data.get('code', '').upper()
        cart_total = Decimal(request.data.get('cart_total', 0))
        
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_valid:
                return Response({
                    'valid': False,
                    'message': 'Coupon is not valid or has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if cart_total < coupon.minimum_order_amount:
                return Response({
                    'valid': False,
                    'message': f'Minimum order amount is ${coupon.minimum_order_amount}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            discount = coupon.calculate_discount(cart_total)
            
            return Response({
                'valid': True,
                'discount_amount': float(discount),
                'message': f'Coupon applied! You save ${discount}'
            })
        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'Invalid coupon code'
            }, status=status.HTTP_404_NOT_FOUND)


class AdvertisementViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for advertisements"""
    serializer_class = AdvertisementSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Advertisement.objects.filter(is_active=True)
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        return queryset.order_by('display_order')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get user profile"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return Response({
        'user': UserSerializer(request.user).data,
        'profile': UserProfileSerializer(profile).data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
