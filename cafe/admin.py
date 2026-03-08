from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count, Sum
from decimal import Decimal
from .models import *

# Custom Admin Actions
@admin.action(description='Mark selected items as available')
def make_available(modeladmin, request, queryset):
    queryset.update(available=True)

@admin.action(description='Mark selected items as unavailable')
def make_unavailable(modeladmin, request, queryset):
    queryset.update(available=False)

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_items_count', 'created_at', 'icon_preview')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Items Count'
    
    def icon_preview(self, obj):
        return format_html('<i class="{}" style="font-size: 16px;"></i>', obj.icon)
    icon_preview.short_description = 'Icon'

# MenuItem Admin
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'get_discounted_price', 'available', 'is_featured', 'item_type', 'created_at')
    list_filter = ('category', 'available', 'is_featured', 'item_type', 'created_at')
    search_fields = ('name', 'description', 'ingredients')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category', 'name')
    actions = [make_available, make_unavailable]
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'ingredients')
        }),
        ('Pricing', {
            'fields': ('price', 'discount')
        }),
        ('Availability', {
            'fields': ('available', 'is_featured', 'item_type')
        }),
        ('Images', {
            'fields': ('image', 'image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_discounted_price(self, obj):
        return obj.discounted_price
    get_discounted_price.short_description = 'Discounted Price'

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'get_orders_count', 'get_wishlist_count', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('user_username', 'user_email', 'phone', 'city')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'date_of_birth')
        }),
        ('Address', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_orders_count(self, obj):
        return obj.user.orders.count()
    get_orders_count.short_description = 'Orders'
    
    def get_wishlist_count(self, obj):
        return obj.user.wishlist_items.count()
    get_wishlist_count.short_description = 'Wishlist Items'

# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'quantity', 'get_total_price', 'saved_for_later', 'is_selected', 'created_at')
    list_filter = ('saved_for_later', 'is_selected', 'created_at')
    search_fields = ('user_username', 'menu_item_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Cart Item', {
            'fields': ('user', 'menu_item', 'quantity')
        }),
        ('Options', {
            'fields': ('saved_for_later', 'is_selected')
        }),
        ('Calculated Fields', {
            'fields': ('get_total_price', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_price(self, obj):
        return obj.total_price
    get_total_price.short_description = 'Total Price'

# Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'price', 'get_total_price')

    def get_total_price(self, obj):
        if obj:
            return obj.total_price
        return 0
    get_total_price.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'delivery_fee', 'status', 'payment_status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user_username', 'user_email', 'phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'get_grand_total')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'notes')
        }),
        ('Pricing', {
            'fields': ('total', 'delivery_fee', 'tax_amount', 'get_grand_total'),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'razorpay_order_id', 'razorpay_payment_id'),
        }),
        ('Customer Details', {
            'fields': ('delivery_address', 'phone', 'estimated_delivery_time'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_grand_total(self, obj):
        if obj:
            return obj.grand_total
        return 0
    get_grand_total.short_description = 'Grand Total'

# OrderItem Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price', 'get_total_price', 'created_at')
    list_filter = ('order__created_at',)
    search_fields = ('order_order_number', 'menu_item_name')
    readonly_fields = ('get_total_price', 'created_at')
    
    fieldsets = (
        ('Order Item Details', {
            'fields': ('order', 'menu_item', 'quantity', 'price')
        }),
        ('Calculated Fields', {
            'fields': ('get_total_price', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_price(self, obj):
        if obj:
            return obj.total_price
        return 0
    get_total_price.short_description = 'Total Price'

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user_username', 'menu_item_name', 'comment')
    readonly_fields = ('created_at',)

# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_username', 'menu_item_name')
    readonly_fields = ('created_at',)

# Rating Admin
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user_username', 'menu_item_name')
    readonly_fields = ('created_at', 'updated_at')

# Coupon Admin
@admin.action(description='Activate selected coupons')
def activate_coupons(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description='Deactivate selected coupons')
def deactivate_coupons(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'minimum_order_amount', 'is_valid', 'is_active', 'used_count', 'created_at')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at')
    actions = [activate_coupons, deactivate_coupons]
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'description', 'discount_type', 'discount_value')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'minimum_order_amount', 'usage_limit')
        }),
        ('Status', {
            'fields': ('is_active', 'used_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# Notification Admin
@admin.action(description='Mark selected notifications as read')
def mark_notifications_read(modeladmin, request, queryset):
    queryset.update(is_read=True)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    actions = [mark_notifications_read]

# DeliveryAddress Admin
@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'city', 'state', 'is_default', 'created_at')
    list_filter = ('is_default', 'state', 'created_at')
    search_fields = ('user__username', 'label', 'city', 'state', 'postal_code')
    readonly_fields = ('created_at',)

# OrderTracking Admin
@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'message', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'message')
    readonly_fields = ('created_at',)

# Advertisement Admin
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'ad_type', 'position', 'is_active', 'is_currently_active', 'display_order', 'created_at')
    list_filter = ('ad_type', 'position', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'subtitle')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('display_order', 'created_at')

# Custom User Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_orders_count', 'date_joined')
    
    def get_orders_count(self, obj):
        if obj:
            return obj.orders.count()
        return 0
    get_orders_count.short_description = 'Orders'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Custom Admin Site Configuration
admin.site.site_header = " Spices of India Cuisine Management System"
admin.site.site_title = "Spices of India Cuisine Management System"
admin.site.index_title = "Welcome to  Spices of India Cuisine Admin Dashboard"