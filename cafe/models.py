from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    icon = models.CharField(max_length=50, default='fa-utensils', help_text="FontAwesome icon class (e.g., fa-pizza-slice, fa-coffee)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('menu') + f'?category={self.slug}'


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="External image URL for menu item")
    description = models.TextField()
    ingredients = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_featured = models.BooleanField(default=False)
    ITEM_TYPES = (
        ('veg', 'Veg'),
        ('non-veg', 'Non-Veg'),
    )
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES, default='veg')
    preparation_time = models.PositiveIntegerField(default=15, help_text="Time in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('menu_item_detail', args=[self.slug])

    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    @property
    def has_discount(self):
        return self.discount > 0

    @property
    def get_image_url(self):
        """Return image URL - either uploaded image or external URL"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        else:
            # Default placeholder image
            return 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop'

    @property
    def is_vegetarian(self):
        """Check if item is vegetarian based on type or category name"""
        # First priority: Explicit non-veg type
        if self.item_type == 'non-veg':
            return False
            
        # Second priority: Category name contains non-veg keywords
        non_veg_keywords = ['non-veg', 'non veg', 'meat', 'chicken', 'fish', 'egg']
        cat_name = self.category.name.lower()
        if any(keyword in cat_name for keyword in non_veg_keywords):
            return False
            
        return True

    @property
    def is_spicy(self):
        """Check if item is spicy based on name or ingredients"""
        spicy_keywords = ['spicy', 'hot', 'chili', 'pepper', 'masala']
        return any(keyword in self.name.lower() or keyword in self.ingredients.lower() 
                  for keyword in spicy_keywords)

    @property
    def is_popular(self):
        """Check if item is popular (featured items are considered popular)"""
        return self.is_featured


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_photos/', default='default-user.png', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    saved_for_later = models.BooleanField(default=False, help_text="Save this item for later purchase")
    is_selected = models.BooleanField(default=True, help_text="Selected for checkout")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'menu_item')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name} x {self.quantity}"

    @property
    def total_price(self):
        if self.menu_item and self.quantity:
            return self.menu_item.discounted_price * self.quantity
        return 0
    
    def get_total_price(self):
        """Method to get total price (same as total_price property)"""
        if self.menu_item and self.quantity:
            return self.menu_item.discounted_price * self.quantity
        return 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
        ('dummy', 'Test Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.TextField()
    phone = models.CharField(max_length=15)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='razorpay')
    
    # Payment Gateway IDs
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    tax_amount = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    @property
    def grand_total(self):
        return self.total + self.delivery_fee

    @property
    def payment_id(self):
        """Return the appropriate payment ID based on payment method"""
        if self.payment_method == 'razorpay' and self.razorpay_payment_id:
            return self.razorpay_payment_id
        return None

    @property
    def total_items(self):
        """Return the total quantity of all items in this order"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def total_price(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu_item', 'order')

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name} - {self.rating} stars"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu_item')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name}"


class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'menu_item')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name} - {self.rating} stars"


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    maximum_discount_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, order_amount):
        if not self.is_valid or order_amount < self.minimum_order_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = order_amount * (self.discount_value / 100)
            if self.maximum_discount_amount:
                discount = min(discount, self.maximum_discount_amount)
        else:
            discount = self.discount_value
        
        return min(discount, order_amount)


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_update', 'Order Update'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
        ('reminder', 'Reminder'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    label = models.CharField(max_length=50, help_text="e.g., Home, Office, etc.")
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.label}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses for this user to not default
            DeliveryAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class OrderTracking(models.Model):
    TRACKING_STATUS_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('preparing', 'Preparing Your Order'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    message = models.TextField(blank=True)
    estimated_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order.order_number} - {self.get_status_display()}"



class Advertisement(models.Model):
    AD_TYPE_CHOICES = [
        ('promo_card', 'Promotional Card'),
        ('banner', 'Banner Ad'),
        ('mini_ad', 'Mini Ad'),
    ]
    
    AD_POSITION_CHOICES = [
        ('home_top', 'Home Page - Top'),
        ('home_middle', 'Home Page - Middle'),
        ('menu_sidebar', 'Menu Page - Sidebar'),
        ('cart_bottom', 'Cart Page - Bottom'),
    ]
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    ad_type = models.CharField(max_length=20, choices=AD_TYPE_CHOICES, default='promo_card')
    position = models.CharField(max_length=20, choices=AD_POSITION_CHOICES, default='home_middle')
    
    # Visual styling
    badge_text = models.CharField(max_length=50, blank=True, help_text="e.g., NEW USER OFFER, LIMITED TIME")
    icon_class = models.CharField(max_length=50, default='fa-gift', help_text="FontAwesome icon class")
    gradient_start = models.CharField(max_length=7, default='#667eea', help_text="Hex color code")
    gradient_end = models.CharField(max_length=7, default='#764ba2', help_text="Hex color code")
    
    # Call to action
    button_text = models.CharField(max_length=50, default='Claim Offer')
    button_url = models.CharField(max_length=200, help_text="URL or Django URL name")
    coupon_code = models.CharField(max_length=50, blank=True, help_text="Optional coupon code to display")
    
    # Additional info
    promo_code_text = models.CharField(max_length=100, blank=True, help_text="e.g., Use Code: FIRST50")
    
    # Status and ordering
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    
    # Scheduling
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
    
    def __str__(self):
        return f"{self.title} ({self.get_ad_type_display()})"
    
    @property
    def is_currently_active(self):
        """Check if ad is active and within date range"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
