from rest_framework import serializers
from django.contrib.auth.models import User
from cafe.models import (
    Category, MenuItem, UserProfile, Cart, Order, OrderItem,
    Review, Wishlist, Rating, Coupon, Notification,
    DeliveryAddress, OrderTracking, Advertisement
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'icon', 'items_count', 'created_at']
    
    def get_items_count(self, obj):
        return obj.items.filter(available=True).count()


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'slug', 'price', 'category', 'category_name',
            'image', 'image_url', 'description', 'ingredients', 'available',
            'discount', 'discounted_price', 'has_discount', 'is_featured',
            'item_type', 'preparation_time', 'average_rating', 'review_count',
            'is_wishlisted', 'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        from django.db.models import Avg
        avg = obj.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, menu_item=obj).exists()
        return False


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True, source='get_total_price')
    
    class Meta:
        model = Cart
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'is_selected', 'saved_for_later', 'total_price', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'menu_item_image', 'quantity', 'price', 'total_price']
    
    def get_menu_item_image(self, obj):
        return obj.menu_item.get_image_url


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_name', 'status', 'status_display',
            'payment_status', 'payment_status_display', 'payment_method',
            'total', 'delivery_fee', 'tax_amount', 'grand_total',
            'delivery_address', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'menu_item', 'menu_item_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class WishlistSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'menu_item', 'menu_item_id', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'menu_item', 'rating', 'created_at']
        read_only_fields = ['user', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    discount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'minimum_order_amount', 'maximum_discount_amount', 'usage_limit',
            'used_count', 'valid_from', 'valid_until', 'is_active', 'is_valid',
            'discount_display'
        ]
    
    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}% off"
        return f"₹{obj.discount_value} off"


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'notification_type_display', 'is_read', 'created_at']


class DeliveryAddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryAddress
        fields = [
            'id', 'label', 'address_line_1', 'address_line_2', 'city',
            'state', 'postal_code', 'phone', 'is_default', 'full_address', 'created_at'
        ]
    
    def get_full_address(self, obj):
        parts = [obj.address_line_1]
        if obj.address_line_2:
            parts.append(obj.address_line_2)
        parts.extend([obj.city, obj.state, obj.postal_code])
        return ', '.join(parts)


class OrderTrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OrderTracking
        fields = ['id', 'order', 'status', 'status_display', 'message', 'estimated_time', 'created_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    ad_type_display = serializers.CharField(source='get_ad_type_display', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    
    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'subtitle', 'description', 'ad_type', 'ad_type_display',
            'position', 'position_display', 'badge_text', 'icon_class',
            'gradient_start', 'gradient_end', 'button_text', 'button_url',
            'coupon_code', 'promo_code_text', 'is_active', 'display_order'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
