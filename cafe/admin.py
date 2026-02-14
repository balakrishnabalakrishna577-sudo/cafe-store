from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Sum
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Count
from datetime import datetime, timedelta
import json

from .models import (
    Category, MenuItem, UserProfile, Cart, Order, OrderItem, 
    Review, Wishlist, Rating, Coupon, Notification, 
    DeliveryAddress, OrderTracking, Advertisement
)


# Custom Admin Site
class CafeAdminSite(admin.AdminSite):
    site_header = "Spices of India Cuisine Admin Panel"
    site_title = "Spices of India Cuisine Admin"
    index_title = "Welcome to Spices of India Cuisine Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.custom_dashboard), name='custom_dashboard'),
            path('analytics/', self.admin_view(self.custom_analytics), name='custom_analytics'),
        ]
        return custom_urls + urls
    
    def custom_dashboard(self, request):
        """Enhanced dashboard with statistics"""
        # Get statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status__in=['pending', 'confirmed', 'preparing']).count()
        completed_orders = Order.objects.filter(status='delivered').count()
        total_revenue = Order.objects.filter(payment_status='completed').aggregate(
            total=Sum('total')
        )['total'] or 0
        
        # Get recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        
        # Get popular items
        popular_items = OrderItem.objects.values('menu_item__name').annotate(
            total_ordered=Sum('quantity')
        ).order_by('-total_ordered')[:5]
        
        # Get menu statistics
        total_items = MenuItem.objects.count()
        available_items = MenuItem.objects.filter(available=True).count()
        categories_count = Category.objects.count()
        
        # Get customer statistics
        total_customers = UserProfile.objects.count()
        
        context = {
            **self.each_context(request),
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders,
            'popular_items': popular_items,
            'total_items': total_items,
            'available_items': available_items,
            'categories_count': categories_count,
            'total_customers': total_customers,
        }
        
        return render(request, 'admin/custom_dashboard.html', context)
    
    def custom_analytics(self, request):
        """Analytics dashboard"""
        # Date range for analytics (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Daily sales data
        daily_sales = []
        for i in range(30):
            date = start_date + timedelta(days=i)
            sales = Order.objects.filter(
                created_at__date=date,
                payment_status='completed'
            ).aggregate(total=Sum('total'))['total'] or 0
            daily_sales.append({
                'date': date.strftime('%Y-%m-%d'),
                'sales': float(sales)
            })
        
        # Category performance
        category_stats = []
        for category in Category.objects.all():
            revenue = OrderItem.objects.filter(
                menu_item__category=category,
                order__payment_status='completed'
            ).aggregate(total=Sum('price'))['total'] or 0
            
            items_sold = OrderItem.objects.filter(
                menu_item__category=category,
                order__payment_status='completed'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            category_stats.append({
                'name': category.name,
                'revenue': float(revenue),
                'items_count': category.items.count(),
                'items_sold': items_sold
            })
        
        # Sort by revenue
        category_stats.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Monthly comparison
        current_month_start = datetime.now().replace(day=1).date()
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        current_month_revenue = Order.objects.filter(
            created_at__date__gte=current_month_start,
            payment_status='completed'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        last_month_revenue = Order.objects.filter(
            created_at__date__gte=last_month_start,
            created_at__date__lt=current_month_start,
            payment_status='completed'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Calculate growth percentage
        if last_month_revenue > 0:
            growth_percentage = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
        else:
            growth_percentage = 100 if current_month_revenue > 0 else 0
        
        # Top performing items
        top_items = OrderItem.objects.filter(
            order__payment_status='completed'
        ).values('menu_item__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_revenue')[:5]
        
        # Order status distribution
        status_distribution = []
        for status_code, status_name in Order.STATUS_CHOICES:
            count = Order.objects.filter(status=status_code).count()
            status_distribution.append({
                'status': status_name,
                'count': count
            })
        
        context = {
            **self.each_context(request),
            'daily_sales': json.dumps(daily_sales),
            'category_stats': category_stats,
            'current_month_revenue': current_month_revenue,
            'last_month_revenue': last_month_revenue,
            'growth_percentage': round(growth_percentage, 1),
            'top_items': top_items,
            'status_distribution': status_distribution,
            'total_revenue_30_days': sum(item['sales'] for item in daily_sales),
            'avg_daily_sales': sum(item['sales'] for item in daily_sales) / 30,
        }
        
        return render(request, 'admin/custom_analytics.html', context)
    
    def index(self, request, extra_context=None):
        """Override index to show custom dashboard"""
        extra_context = extra_context or {}
        
        # Add quick stats to the main index
        extra_context['total_orders'] = Order.objects.count()
        extra_context['pending_orders'] = Order.objects.filter(status__in=['pending', 'confirmed', 'preparing']).count()
        extra_context['total_revenue'] = Order.objects.filter(payment_status='completed').aggregate(
            total=Sum('total')
        )['total'] or 0
        extra_context['total_customers'] = UserProfile.objects.count()
        
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = CafeAdminSite(name='cafe_admin')


# Inline UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['phone', 'address', 'city', 'postal_code', 'date_of_birth', 'image']


# Custom User Admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'get_order_count', 'get_total_spent']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)
    
    def get_order_count(self, obj):
        count = Order.objects.filter(user=obj).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    get_order_count.short_description = 'Orders'
    
    def get_total_spent(self, obj):
        total = Order.objects.filter(user=obj, payment_status='completed').aggregate(
            total=Sum('total')
        )['total'] or 0
        formatted_total = f'{total:.2f}'
        return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', formatted_total)
    get_total_spent.short_description = 'Total Spent'


# Category Admin
@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon_preview', 'get_item_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    fields = ['name', 'slug', 'description', 'image', 'icon']
    ordering = ['name']
    
    def get_item_count(self, obj):
        count = obj.items.count()
        return format_html('<span class="badge badge-info">{}</span>', count)
    get_item_count.short_description = 'Total Items'
    
    def icon_preview(self, obj):
        return format_html('<i class="fas {} fa-2x" style="color: #ff4d4d;"></i>', obj.icon)
    icon_preview.short_description = 'Icon Preview'
    
    class Meta:
        verbose_name = "📁 Category"
        verbose_name_plural = "📁 Categories"


# MenuItem Admin
@admin.register(MenuItem, site=admin_site)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['get_image_preview', 'name', 'category', 'price', 'get_discounted_price', 'get_discount_badge', 'available', 'item_type', 'is_featured', 'created_at']
    list_filter = ['category', 'available', 'item_type', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'ingredients']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['available', 'is_featured']
    readonly_fields = ['created_at', 'updated_at', 'get_image_preview']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'ingredients')
        }),
        ('Pricing', {
            'fields': ('price', 'discount'),
            'description': 'Set the base price and discount percentage'
        }),
        ('Images', {
            'fields': ('get_image_preview', 'image', 'image_url'),
            'description': 'Upload an image or provide an image URL'
        }),
        ('Settings', {
            'fields': ('item_type', 'available', 'is_featured', 'preparation_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.image_url)
        return format_html('<span style="color: #999;">{}</span>', 'No image')
    get_image_preview.short_description = 'Image'
    
    def get_discounted_price(self, obj):
        if obj.discount > 0:
            return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', obj.discounted_price)
        return format_html('<span>₹{}</span>', obj.discounted_price)
    get_discounted_price.short_description = 'Final Price'
    
    def get_discount_badge(self, obj):
        if obj.discount > 0:
            return format_html('<span class="badge badge-danger">{}% OFF</span>', obj.discount)
        return format_html('<span class="badge badge-secondary">{}</span>', 'No Discount')
    get_discount_badge.short_description = 'Discount'
    
    class Meta:
        verbose_name = "🍽️ Menu Item"
        verbose_name_plural = "🍽️ Menu Items"


# UserProfile Admin
@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_image_preview', 'phone', 'city', 'get_order_count', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_filter = ['city', 'created_at']
    readonly_fields = ['created_at', 'get_image_preview']
    ordering = ['-created_at']
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />', obj.image.url)
        return format_html('<span style="color: #999;"><i class="fas fa-user-circle fa-2x"></i></span>')
    get_image_preview.short_description = 'Photo'
    
    def get_order_count(self, obj):
        count = Order.objects.filter(user=obj.user).count()
        return format_html('<span class="badge badge-info">{}</span>', count)
    get_order_count.short_description = 'Orders'
    
    class Meta:
        verbose_name = "👤 User Profile"
        verbose_name_plural = "👤 User Profiles"


# Cart Admin
@admin.register(Cart, site=admin_site)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'quantity', 'get_selected_badge', 'get_saved_badge', 'get_total_price', 'created_at']
    list_filter = ['is_selected', 'saved_for_later', 'created_at']
    search_fields = ['user__username', 'menu_item__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_selected_badge(self, obj):
        if obj.is_selected:
            return format_html('<span class="badge badge-success"><i class="fas fa-check"></i>{}</span>', '')
        return format_html('<span class="badge badge-secondary"><i class="fas fa-times"></i>{}</span>', '')
    get_selected_badge.short_description = 'Selected'
    
    def get_saved_badge(self, obj):
        if obj.saved_for_later:
            return format_html('<span class="badge badge-warning"><i class="fas fa-bookmark"></i> {}</span>', 'Saved')
        return format_html('<span class="badge badge-secondary">{}</span>', '-')
    get_saved_badge.short_description = 'Saved'
    
    def get_total_price(self, obj):
        return format_html('<span style="font-weight: bold;">₹{}</span>', obj.total_price)
    get_total_price.short_description = 'Total Price'
    
    class Meta:
        verbose_name = "🛒 Cart Item"
        verbose_name_plural = "🛒 Cart Items"


# OrderItem Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['menu_item', 'quantity', 'price', 'get_total_price']
    
    def get_total_price(self, obj):
        return f"₹{obj.total_price}"
    get_total_price.short_description = 'Total'


# Order Admin
@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'get_status_badge', 'get_payment_badge', 'payment_method', 'get_total_display', 'get_grand_total', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'phone', 'notes', 'estimated_delivery_time')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'razorpay_order_id', 'razorpay_payment_id')
        }),
        ('Pricing', {
            'fields': ('total', 'delivery_fee', 'tax_amount')
        }),
    )
    
    def get_status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'preparing': 'primary',
            'out_for_delivery': 'info',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    get_status_badge.short_description = 'Status'
    
    def get_payment_badge(self, obj):
        colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'refunded': 'info'
        }
        color = colors.get(obj.payment_status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_payment_status_display())
    get_payment_badge.short_description = 'Payment'
    
    def get_total_display(self, obj):
        return format_html('<span style="font-weight: bold;">₹{}</span>', obj.total)
    get_total_display.short_description = 'Subtotal'
    
    def get_grand_total(self, obj):
        return format_html('<span style="color: green; font-weight: bold; font-size: 1.1em;">₹{}</span>', obj.grand_total)
    get_grand_total.short_description = 'Grand Total'
    
    class Meta:
        verbose_name = "🛒 Order"
        verbose_name_plural = "🛒 Orders"


# OrderItem Admin
@admin.register(OrderItem, site=admin_site)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price', 'get_total_price']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'menu_item__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_total_price(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', obj.total_price)
    get_total_price.short_description = 'Total Price'
    
    class Meta:
        verbose_name = "📦 Order Item"
        verbose_name_plural = "📦 Order Items"


# Review Admin
@admin.register(Review, site=admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'get_rating_stars', 'get_comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'menu_item__name', 'comment']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 1.2em;">{}</span>', stars)
    get_rating_stars.short_description = 'Rating'
    
    def get_comment_preview(self, obj):
        if obj.comment:
            preview = obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
            return format_html('<span style="color: #666;">{}</span>', preview)
        return format_html('<span style="color: #999;">{}</span>', 'No comment')
    get_comment_preview.short_description = 'Comment'
    
    class Meta:
        verbose_name = "⭐ Review"
        verbose_name_plural = "⭐ Reviews"


# Rating Admin
@admin.register(Rating, site=admin_site)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'get_rating_stars', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'menu_item__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_rating_stars(self, obj):
        stars = '⭐' * obj.rating
        empty_stars = '☆' * (5 - obj.rating)
        return format_html('<span style="font-size: 1.2em;">{}{}</span>', stars, empty_stars)
    get_rating_stars.short_description = 'Rating'
    
    class Meta:
        verbose_name = "⭐ Rating"
        verbose_name_plural = "⭐ Ratings"


# Wishlist Admin
@admin.register(Wishlist, site=admin_site)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'get_item_price', 'get_item_available', 'created_at']
    list_filter = ['created_at', 'menu_item__available']
    search_fields = ['user__username', 'menu_item__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_item_price(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', obj.menu_item.discounted_price)
    get_item_price.short_description = 'Price'
    
    def get_item_available(self, obj):
        if obj.menu_item.available:
            return format_html('<span class="badge badge-success"><i class="fas fa-check"></i> {}</span>', 'Available')
        return format_html('<span class="badge badge-danger"><i class="fas fa-times"></i> {}</span>', 'Unavailable')
    get_item_available.short_description = 'Status'
    
    class Meta:
        verbose_name = "❤️ Wishlist Item"
        verbose_name_plural = "❤️ Wishlist Items"


# Coupon Admin
@admin.register(Coupon, site=admin_site)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'get_discount_display', 'is_active', 'get_is_valid_status', 'get_usage_display', 'valid_from', 'valid_until']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'description', 'is_active'),
            'description': 'Basic coupon information'
        }),
        ('Discount Settings', {
            'fields': ('discount_type', 'discount_value', 'minimum_order_amount', 'maximum_discount_amount'),
            'description': 'Configure discount rules'
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'used_count'),
            'description': 'Set usage restrictions'
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until'),
            'description': 'Define when this coupon is active'
        }),
    )
    
    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html('<span class="badge badge-success">{}% OFF</span>', obj.discount_value)
        else:
            return format_html('<span class="badge badge-success">₹{} OFF</span>', obj.discount_value)
    get_discount_display.short_description = 'Discount'
    
    def get_is_valid_status(self, obj):
        if obj.is_valid:
            return format_html('<span class="badge badge-success"><i class="fas fa-check"></i> {}</span>', 'Valid')
        return format_html('<span class="badge badge-danger"><i class="fas fa-times"></i> {}</span>', 'Invalid')
    get_is_valid_status.short_description = 'Status'
    
    def get_usage_display(self, obj):
        if obj.usage_limit:
            percentage = (obj.used_count / obj.usage_limit) * 100
            color = 'success' if percentage < 50 else 'warning' if percentage < 80 else 'danger'
            return format_html(
                '<span class="badge badge-{}">{} / {}</span>',
                color, obj.used_count, obj.usage_limit
            )
        return format_html('<span class="badge badge-info">{} / Unlimited</span>', obj.used_count)
    get_usage_display.short_description = 'Usage'
    
    class Meta:
        verbose_name = "🎟️ Coupon"
        verbose_name_plural = "🎟️ Coupons"


# Notification Admin
@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'get_type_badge', 'get_read_status', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def get_type_badge(self, obj):
        colors = {
            'order_update': 'primary',
            'promotion': 'success',
            'info': 'info',
            'warning': 'warning',
            'error': 'danger'
        }
        color = colors.get(obj.notification_type, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_notification_type_display())
    get_type_badge.short_description = 'Type'
    
    def get_read_status(self, obj):
        if obj.is_read:
            return format_html('<span class="badge badge-secondary"><i class="fas fa-envelope-open"></i> {}</span>', 'Read')
        return format_html('<span class="badge badge-primary"><i class="fas fa-envelope"></i> {}</span>', 'Unread')
    get_read_status.short_description = 'Status'
    
    class Meta:
        verbose_name = "🔔 Notification"
        verbose_name_plural = "🔔 Notifications"


# DeliveryAddress Admin
@admin.register(DeliveryAddress, site=admin_site)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'get_address_preview', 'city', 'state', 'postal_code', 'get_default_badge', 'created_at']
    list_filter = ['is_default', 'city', 'state', 'created_at']
    search_fields = ['user__username', 'label', 'city', 'address_line_1']
    readonly_fields = ['created_at']
    ordering = ['-is_default', '-created_at']
    
    def get_default_badge(self, obj):
        if obj.is_default:
            return format_html('<span class="badge badge-success"><i class="fas fa-star"></i> {}</span>', 'Default')
        return format_html('<span class="badge badge-secondary">{}</span>', '-')
    get_default_badge.short_description = 'Default'
    
    def get_address_preview(self, obj):
        preview = obj.address_line_1[:30] + '...' if len(obj.address_line_1) > 30 else obj.address_line_1
        return format_html('<span style="color: #666;">{}</span>', preview)
    get_address_preview.short_description = 'Address'
    
    class Meta:
        verbose_name = "📍 Delivery Address"
        verbose_name_plural = "📍 Delivery Addresses"


# OrderTracking Admin
@admin.register(OrderTracking, site=admin_site)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'get_status_badge', 'message', 'estimated_time', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def get_status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'preparing': 'primary',
            'out_for_delivery': 'info',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    get_status_badge.short_description = 'Status'
    
    class Meta:
        verbose_name = "🚚 Order Tracking"
        verbose_name_plural = "🚚 Order Tracking"


# Unregister default User admin and register custom one
admin_site.register(User, CustomUserAdmin)

# All other models are registered using @admin.register decorators above
# No need to register them again here



# Advertisement Admin
@admin.register(Advertisement, site=admin_site)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_type_badge', 'get_position_badge', 'get_active_status', 'display_order', 'get_date_range', 'created_at']
    list_filter = ['ad_type', 'position', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description', 'coupon_code']
    list_editable = ['display_order']
    ordering = ['display_order', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'description', 'ad_type', 'position')
        }),
        ('Visual Design', {
            'fields': ('badge_text', 'icon_class', 'gradient_start', 'gradient_end'),
            'description': 'Customize the appearance of your advertisement'
        }),
        ('Call to Action', {
            'fields': ('button_text', 'button_url', 'coupon_code', 'promo_code_text')
        }),
        ('Status & Scheduling', {
            'fields': ('is_active', 'display_order', 'start_date', 'end_date')
        }),
    )
    
    def get_type_badge(self, obj):
        colors = {
            'promo_card': '#667eea',
            'banner': '#f5576c',
            'mini_ad': '#4facfe',
        }
        color = colors.get(obj.ad_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_ad_type_display()
        )
    get_type_badge.short_description = 'Type'
    
    def get_position_badge(self, obj):
        return format_html(
            '<span style="background: #e9ecef; color: #495057; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 500;">{}</span>',
            obj.get_position_display()
        )
    get_position_badge.short_description = 'Position'
    
    def get_active_status(self, obj):
        if obj.is_currently_active:
            return format_html(
                '<span style="color: #28a745; font-weight: 600;"><i class="fas fa-check-circle"></i> {}</span>',
                'Active'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: 600;"><i class="fas fa-times-circle"></i> {}</span>',
            'Inactive'
        )
    get_active_status.short_description = 'Status'
    
    def get_date_range(self, obj):
        if obj.start_date and obj.end_date:
            return format_html(
                '<small>{} to {}</small>',
                obj.start_date.strftime('%Y-%m-%d'),
                obj.end_date.strftime('%Y-%m-%d')
            )
        elif obj.start_date:
            return format_html(
                '<small>From {}</small>', 
                obj.start_date.strftime('%Y-%m-%d')
            )
        elif obj.end_date:
            return format_html(
                '<small>Until {}</small>', 
                obj.end_date.strftime('%Y-%m-%d')
            )
        return format_html(
            '<small style="color: #6c757d;">{}</small>',
            'No date limit'
        )
    get_date_range.short_description = 'Schedule'
    
    actions = ['activate_ads', 'deactivate_ads', 'duplicate_ad']
    
    def activate_ads(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} advertisement(s) activated successfully.')
    activate_ads.short_description = 'Activate selected advertisements'
    
    def deactivate_ads(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} advertisement(s) deactivated successfully.')
    deactivate_ads.short_description = 'Deactivate selected advertisements'
    
    def duplicate_ad(self, request, queryset):
        for ad in queryset:
            ad.pk = None
            ad.title = f"{ad.title} (Copy)"
            ad.is_active = False
            ad.save()
        self.message_user(request, f'{queryset.count()} advertisement(s) duplicated successfully.')
    duplicate_ad.short_description = 'Duplicate selected advertisements'
