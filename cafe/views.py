from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    Category, MenuItem, Cart, Order, OrderItem, UserProfile, Review,
    Wishlist, Rating, Coupon, Notification, DeliveryAddress, OrderTracking
)
from .forms import (
    CustomUserCreationForm, UserProfileForm, UserUpdateForm, CheckoutForm, ReviewForm,
    DeliveryAddressForm, CouponForm, RatingForm
)

# Handle missing payment gateways gracefully
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
    # Get Razorpay credentials with defaults
    razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    razorpay_key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if razorpay_key_id and razorpay_key_secret:
        razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
    else:
        razorpay_client = None
except (ImportError, AttributeError, Exception):
    RAZORPAY_AVAILABLE = False
    razorpay_client = None


def home_view(request):
    """Simple function-based view for homepage"""
    featured_items = MenuItem.objects.filter(is_featured=True, available=True)[:6]
    categories = Category.objects.all()[:4]
    total_items = MenuItem.objects.filter(available=True).count()
    total_categories = Category.objects.count()
    
    # Recently added items (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    recent_date = timezone.now() - timedelta(days=7)
    recently_added = MenuItem.objects.filter(
        available=True,
        created_at__gte=recent_date
    ).order_by('-created_at')[:6]
    
    context = {
        'featured_items': featured_items,
        'categories': categories,
        'total_items': total_items,
        'total_categories': total_categories,
        'recently_added': recently_added,
    }
    return render(request, 'cafe/index.html', context)


def about_view(request):
    """About page view"""
    return render(request, 'cafe/about.html')


def contact_view(request):
    """Contact page view"""
    return render(request, 'cafe/contact.html')


def gallery_view(request):
    """Gallery page view"""
    return render(request, 'cafe/gallery.html')


@login_required
def user_dashboard(request):
    """Enhanced user dashboard with comprehensive overview"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user's orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Order statistics
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(
        user=request.user, 
        status__in=['pending', 'confirmed', 'preparing', 'out_for_delivery']
    ).count()
    completed_orders = Order.objects.filter(user=request.user, status='delivered').count()
    cancelled_orders = Order.objects.filter(user=request.user, status='cancelled').count()
    
    # Total spent and average order value
    total_spent = Order.objects.filter(
        user=request.user, 
        payment_status='completed'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    avg_order_value = total_spent / total_orders if total_orders > 0 else Decimal('0.00')
    
    # Wishlist count
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    # Cart count and value
    cart_items = Cart.objects.filter(user=request.user, saved_for_later=False).select_related('menu_item')
    cart_count = cart_items.count()
    cart_value = sum(item.total_price for item in cart_items)
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Delivery addresses (show default first, then most recently created)
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')[:3]
    total_addresses = DeliveryAddress.objects.filter(user=request.user).count()
    
    # Favorite items (most ordered) - Get actual MenuItem objects
    from django.db.models import F
    favorite_item_ids = OrderItem.objects.filter(
        order__user=request.user
    ).values('menu_item_id').annotate(
        order_count=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-order_count')[:6].values_list('menu_item_id', flat=True)
    
    # Get the actual MenuItem objects with their order counts
    favorite_items = []
    for item_id in favorite_item_ids:
        menu_item = MenuItem.objects.get(id=item_id)
        order_stats = OrderItem.objects.filter(
            order__user=request.user,
            menu_item_id=item_id
        ).aggregate(
            order_count=Count('id'),
            total_quantity=Sum('quantity')
        )
        favorite_items.append({
            'menu_item': menu_item,
            'order_count': order_stats['order_count'],
            'total_quantity': order_stats['total_quantity']
        })
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    recent_activity_count = Order.objects.filter(
        user=request.user,
        created_at__gte=thirty_days_ago
    ).count()
    
    last_week_orders = Order.objects.filter(
        user=request.user,
        created_at__gte=seven_days_ago
    ).count()
    
    # Monthly spending trend (last 6 months)
    monthly_spending = []
    for i in range(5, -1, -1):
        month_start = timezone.now() - timedelta(days=30 * (i + 1))
        month_end = timezone.now() - timedelta(days=30 * i)
        month_total = Order.objects.filter(
            user=request.user,
            created_at__gte=month_start,
            created_at__lt=month_end,
            payment_status='completed'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        monthly_spending.append(float(month_total))
    
    # Order status breakdown
    status_breakdown = {
        'pending': Order.objects.filter(user=request.user, status='pending').count(),
        'confirmed': Order.objects.filter(user=request.user, status='confirmed').count(),
        'preparing': Order.objects.filter(user=request.user, status='preparing').count(),
        'out_for_delivery': Order.objects.filter(user=request.user, status='out_for_delivery').count(),
        'delivered': completed_orders,
        'cancelled': cancelled_orders,
    }
    
    # Loyalty points (based on total spent)
    loyalty_points = int(total_spent / 10)  # 1 point per ₹10 spent
    next_reward_points = ((loyalty_points // 100) + 1) * 100
    points_to_next_reward = next_reward_points - loyalty_points
    
    # User profile completion
    profile_completion = 0
    try:
        profile = request.user.userprofile
        if profile.phone:
            profile_completion += 20
        if profile.address:
            profile_completion += 20
        if profile.image:
            profile_completion += 20
        if delivery_addresses.exists():
            profile_completion += 20
        if total_orders > 0:
            profile_completion += 20
    except UserProfile.DoesNotExist:
        pass
    
    # Recommended items (based on favorites and popular items)
    favorite_item_ids_for_exclusion = [item['menu_item'].id for item in favorite_items] if favorite_items else []
    recommended_items = MenuItem.objects.filter(
        available=True,
        is_featured=True
    ).exclude(
        id__in=favorite_item_ids_for_exclusion
    )[:4]
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
        'cart_value': cart_value,
        'recent_notifications': recent_notifications,
        'unread_notifications': unread_notifications,
        'delivery_addresses': delivery_addresses,
        'total_addresses': total_addresses,
        'favorite_items': favorite_items,
        'recent_activity_count': recent_activity_count,
        'last_week_orders': last_week_orders,
        'monthly_spending': monthly_spending,
        'status_breakdown': status_breakdown,
        'loyalty_points': loyalty_points,
        'points_to_next_reward': points_to_next_reward,
        'profile_completion': profile_completion,
        'recommended_items': recommended_items,
    }
    return render(request, 'cafe/dashboard.html', context)

    from django.utils import timezone
    from datetime import timedelta
    recent_date = timezone.now() - timedelta(days=7)
    recently_added = MenuItem.objects.filter(
        available=True,
        created_at__gte=recent_date
    ).order_by('-created_at')[:6]
    
    context = {
        'featured_items': featured_items,
        'categories': categories,
        'total_items': total_items,
        'total_categories': total_categories,
        'recently_added': recently_added,
    }
    return render(request, 'cafe/index.html', context)


class MenuView(ListView):
    model = MenuItem
    template_name = 'cafe/menu.html'
    context_object_name = 'menu_items'
    paginate_by = 12

    def get_queryset(self):
        queryset = MenuItem.objects.filter(available=True)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ingredients__icontains=search_query)
            )
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Veg/Non-Veg filter
        veg_type = self.request.GET.get('veg_type')
        if veg_type:
            queryset = queryset.filter(item_type=veg_type)
        
        # Sort by
        sort_by = self.request.GET.get('sort', 'category')
        
        # Annotate with discounted price for proper sorting
        from django.db.models import F, ExpressionWrapper, DecimalField
        queryset = queryset.annotate(
            actual_price=ExpressionWrapper(
                F('price') - (F('price') * F('discount') / 100),
                output_field=DecimalField()
            )
        )

        if sort_by == 'price_low':
            queryset = queryset.order_by('actual_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-actual_price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'category':
            queryset = queryset.order_by('category__name', 'name')
        elif sort_by == 'popularity':
            queryset = queryset.order_by('-is_featured', 'name')
        else:
            queryset = queryset.order_by('name')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_category = self.request.GET.get('category', '')
        sort_by = self.request.GET.get('sort', 'category')
        current_veg_type = self.request.GET.get('veg_type', '')
        
        # Add selected flag to each category
        categories = Category.objects.all()
        for category in categories:
            category.is_selected = category.slug == current_category
        
        # Create sort options with selected flags
        sort_options = [
            {'value': 'name', 'label': 'Alphabetical (A-Z)', 'selected': sort_by == 'name'},
            {'value': 'category', 'label': 'By Category', 'selected': sort_by == 'category'},
            {'value': 'popularity', 'label': 'Popularity', 'selected': sort_by == 'popularity'},
            {'value': 'price_low', 'label': 'Price: Low to High', 'selected': sort_by == 'price_low'},
            {'value': 'price_high', 'label': 'Price: High to Low', 'selected': sort_by == 'price_high'},
            {'value': 'newest', 'label': 'Newest First', 'selected': sort_by == 'newest'},
        ]
        
        # Determine if any filters are currently active to show "Reset All Filters"
        search_query = self.request.GET.get('search', '')
        has_active_filters = any([
            current_category,
            self.request.GET.get('min_price'),
            self.request.GET.get('max_price'),
            search_query,
            sort_by and sort_by != 'category'
        ])
        
        context['categories'] = categories
        context['current_category'] = current_category
        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['sort_options'] = sort_options
        context['has_active_filters'] = has_active_filters
        return context


class MenuItemDetailView(DetailView):
    model = MenuItem
    template_name = 'cafe/menu_item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()[:5]
        context['avg_rating'] = self.object.reviews.aggregate(Avg('rating'))['rating__avg']
        context['related_items'] = MenuItem.objects.filter(
            category=self.object.category,
            available=True
        ).exclude(id=self.object.id)[:4]
        
        # Track recently viewed items in session
        if 'recently_viewed' not in self.request.session:
            self.request.session['recently_viewed'] = []
        
        recently_viewed = self.request.session['recently_viewed']
        item_id = str(self.object.id)
        
        # Remove if already exists and add to front
        if item_id in recently_viewed:
            recently_viewed.remove(item_id)
        recently_viewed.insert(0, item_id)
        
        # Keep only last 10 items
        recently_viewed = recently_viewed[:10]
        self.request.session['recently_viewed'] = recently_viewed
        self.request.session.modified = True
        
        # Get recently viewed items
        recently_viewed_ids = [int(id) for id in recently_viewed if id != item_id]
        if recently_viewed_ids:
            context['recently_viewed_items'] = MenuItem.objects.filter(
                id__in=recently_viewed_ids[:4],
                available=True
            )
        else:
            context['recently_viewed_items'] = MenuItem.objects.none()
        
        return context


@require_POST
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login to add items to cart',
            'redirect': '/login/'
        })
    
    menu_item_id = request.POST.get('menu_item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    menu_item = get_object_or_404(MenuItem, id=menu_item_id, available=True)
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        menu_item=menu_item,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.is_selected = True
        cart_item.save()
    
    cart_count = Cart.objects.filter(user=request.user).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    return JsonResponse({
        'success': True,
        'message': f'{menu_item.name} added to cart!',
        'cart_count': cart_count,
        'item_name': menu_item.name,
        'item_image': menu_item.get_image_url
    })


@login_required
def cart_view(request):
    # Separate active cart items from saved for later
    cart_items = Cart.objects.filter(user=request.user, saved_for_later=False).select_related('menu_item')
    saved_items = Cart.objects.filter(user=request.user, saved_for_later=True).select_related('menu_item')
    
    # Calculate counts and totals in the view for template stability
    selected_items = cart_items.filter(is_selected=True)
    cart_count = cart_items.count()
    selected_count = selected_items.count()
    
    total = sum(item.total_price for item in selected_items)
    delivery_fee = Decimal('5.00')
    grand_total = total + delivery_fee
    
    context = {
        'cart_items': cart_items,
        'saved_items': saved_items,
        'cart_count': cart_count,
        'selected_count': selected_count,
        'total': total,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
    }
    return render(request, 'cafe/cart.html', context)


@require_POST
def update_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login to update cart',
            'redirect': '/login/'
        })
    
    try:
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not cart_item_id:
            return JsonResponse({
                'success': False,
                'message': 'Cart item ID is required'
            })
        
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        
        # Calculate item total before any changes
        item_total = 0
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            item_total = cart_item.get_total_price()
        else:
            cart_item.delete()
        
        # Calculate updated totals
        cart_items = Cart.objects.filter(user=request.user, saved_for_later=False, is_selected=True)
        cart_total = sum(item.get_total_price() for item in cart_items)
        delivery_fee = 5 if cart_total > 0 else 0
        total = cart_total + delivery_fee
        cart_count = cart_items.count()
        
        return JsonResponse({
            'success': True,
            'item_total': float(item_total),
            'cart_total': float(cart_total),
            'delivery_fee': float(delivery_fee),
            'total': float(total),
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@require_POST
def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login to remove items',
            'redirect': '/login/'
        })
    
    try:
        cart_item_id = request.POST.get('cart_item_id')
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.delete()
        
        # Calculate updated totals
        cart_items = Cart.objects.filter(user=request.user, saved_for_later=False, is_selected=True)
        cart_total = sum(item.get_total_price() for item in cart_items)
        delivery_fee = 5 if cart_total > 0 else 0
        total = cart_total + delivery_fee
        cart_count = cart_items.count()
        
        return JsonResponse({
            'success': True,
            'cart_total': float(cart_total),
            'delivery_fee': float(delivery_fee),
            'total': float(total),
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_POST
def toggle_cart_item_selection(request):
    cart_item_id = request.POST.get('cart_item_id')
    is_selected = request.POST.get('is_selected') == 'true'
    
    if cart_item_id == 'all':
        Cart.objects.filter(user=request.user, saved_for_later=False).update(is_selected=is_selected)
    else:
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.is_selected = is_selected
        cart_item.save()
    
    return JsonResponse({'success': True})


@login_required
def checkout_view(request):
    # Only get selected cart items (not saved for later and is_selected=True)
    cart_items = Cart.objects.filter(user=request.user, saved_for_later=False, is_selected=True).select_related('menu_item')
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    total = sum(item.total_price for item in cart_items)
    delivery_fee = Decimal('5.00')
    grand_total = total + delivery_fee
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                # Create order first
                order = form.save(commit=False)
                order.user = request.user
                order.total = total
                order.delivery_fee = delivery_fee
                order.tax_amount = Decimal('0.00')  # No tax
                # Save special instructions from notes field
                order.special_instructions = form.cleaned_data.get('notes', '')
                # Calculate estimated delivery time (30-45 minutes from now)
                from django.utils import timezone
                from datetime import timedelta
                import random
                delivery_minutes = random.randint(30, 45)
                order.estimated_delivery_time = timezone.now() + timedelta(minutes=delivery_minutes)
                order.save()
                
                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=cart_item.menu_item,
                        quantity=cart_item.quantity,
                        price=cart_item.menu_item.discounted_price
                    )
                
                # Handle payment based on method
                payment_method = request.POST.get('payment_method', 'razorpay')
                
                if payment_method == 'razorpay' and RAZORPAY_AVAILABLE and razorpay_client:
                    # Create Razorpay order
                    razorpay_order = razorpay_client.order.create({
                        'amount': int(grand_total * 100),  # Convert to paise
                        'currency': 'INR',
                        'receipt': f'order_{order.order_number}',
                        'notes': {
                            'user_id': str(request.user.id),
                            'user_email': request.user.email,
                            'order_number': order.order_number,
                        }
                    })
                    
                    order.razorpay_order_id = razorpay_order['id']
                    order.payment_status = 'pending'
                    order.save()
                    
                    # Handle payment verification
                    razorpay_payment_id = request.POST.get('razorpay_payment_id')
                    razorpay_signature = request.POST.get('razorpay_signature')
                    
                    if razorpay_payment_id and razorpay_signature:
                        # Verify payment signature
                        try:
                            razorpay_client.utility.verify_payment_signature({
                                'razorpay_order_id': razorpay_order['id'],
                                'razorpay_payment_id': razorpay_payment_id,
                                'razorpay_signature': razorpay_signature
                            })
                            
                            # Payment successful
                            order.razorpay_payment_id = razorpay_payment_id
                            order.payment_status = 'completed'
                            order.save()
                            
                            # Clear only active and selected cart items
                            Cart.objects.filter(user=request.user, saved_for_later=False, is_selected=True).delete()
                            
                            messages.success(request, f'Order #{order.order_number} placed successfully!')
                            return redirect('order_detail', order_number=order.order_number)
                            
                        except razorpay.errors.SignatureVerificationError:
                            order.payment_status = 'failed'
                            order.save()
                            messages.error(request, 'Payment verification failed. Please try again.')
                    else:
                        # Return order details for payment processing
                        context = {
                            'order': order,
                            'razorpay_order_id': razorpay_order['id'],
                            'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
                            'amount': int(grand_total * 100),
                            'currency': 'INR',
                            'user_name': request.user.get_full_name() or request.user.username,
                            'user_email': request.user.email,
                            'user_phone': getattr(request.user.userprofile, 'phone', '') if hasattr(request.user, 'userprofile') else '',
                        }
                        return render(request, 'cafe/payment_process.html', context)
                
                elif payment_method == 'cod':
                    # Cash on Delivery
                    order.payment_method = 'cod'
                    order.payment_status = 'pending'
                    order.save()
                    
                    # Clear cart
                    cart_items.delete()
                    
                    messages.success(request, f'Order #{order.order_number} placed successfully! Pay on delivery.')
                    return redirect('order_detail', order_number=order.order_number)
                
                else:
                    # Fallback to dummy payment (for testing)
                    order.payment_method = 'dummy'
                    order.payment_status = 'completed'
                    order.razorpay_payment_id = f'dummy_pay_{order.order_number}'
                    order.save()
                    
                    # Clear cart
                    cart_items.delete()
                    
                    messages.success(request, f'Order #{order.order_number} placed successfully! (Test Mode)')
                    return redirect('order_detail', order_number=order.order_number)
                
            except Exception as e:
                messages.error(request, f'Payment processing failed: {str(e)}')
                
    else:
        form = CheckoutForm()
        
        # Pre-fill form with default delivery address
        try:
            default_address = DeliveryAddress.objects.filter(user=request.user, is_default=True).first()
            if default_address:
                # Format the full address
                address_parts = [default_address.address_line_1]
                if default_address.address_line_2:
                    address_parts.append(default_address.address_line_2)
                address_parts.append(f"{default_address.city}, {default_address.state} {default_address.postal_code}")
                
                form.initial = {
                    'delivery_address': '\n'.join(address_parts),
                    'phone': default_address.phone,
                }
            else:
                # Fallback to user profile data if no default address
                try:
                    profile = request.user.userprofile
                    form.initial = {
                        'delivery_address': profile.address,
                        'phone': profile.phone,
                    }
                except UserProfile.DoesNotExist:
                    pass
        except Exception:
            # Fallback to user profile data
            try:
                profile = request.user.userprofile
                form.initial = {
                    'delivery_address': profile.address,
                    'phone': profile.phone,
                }
            except UserProfile.DoesNotExist:
                pass
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'razorpay_available': RAZORPAY_AVAILABLE,
    }
    return render(request, 'cafe/checkout.html', context)


@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__menu_item')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj,
    }
    return render(request, 'cafe/orders.html', context)


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'cafe/order_detail.html', {'order': order})


@login_required
@require_POST
def delete_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Only allow deletion of delivered or cancelled orders
    if order.status not in ['delivered', 'cancelled']:
        return JsonResponse({
            'success': False,
            'message': 'Only delivered or cancelled orders can be deleted.'
        })
    
    order_number = order.order_number
    
    # Delete related order items first
    order.items.all().delete()
    
    # Then delete the order
    order.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Order {order_number} deleted successfully.'
    })


@login_required
@require_POST
def cancel_order(request, order_number):
    """Allow user to cancel their own order if it's still pending"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if order.status != 'pending':
        return JsonResponse({
            'success': False,
            'message': f'Order cannot be cancelled as it is already {order.get_status_display().lower()}.'
        })
    
    order.status = 'cancelled'
    order.save()
    
    # Create notification for user
    from .models import Notification
    Notification.objects.create(
        user=request.user,
        title='Order Cancelled',
        message=f'Your order #{order.order_number} has been cancelled successfully.',
        notification_type='order_update'
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Order #{order.order_number} has been cancelled.'
    })


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully!')
        return response





def search_menu(request):
    query = request.GET.get('q', '')
    if query:
        items = MenuItem.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            available=True
        )[:10]
        
        results = [{
            'id': item.id,
            'name': item.name,
            'price': str(item.discounted_price),
            'image': item.get_image_url,
            'url': item.get_absolute_url(),
        } for item in items]
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})

# New Feature Views

@login_required
@require_POST
def toggle_wishlist(request):
    """Toggle item in user's wishlist"""
    menu_item_id = request.POST.get('menu_item_id')
    menu_item = get_object_or_404(MenuItem, id=menu_item_id, available=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        menu_item=menu_item
    )
    
    if not created:
        wishlist_item.delete()
        is_wishlisted = False
        message = f'{menu_item.name} removed from wishlist'
    else:
        is_wishlisted = True
        message = f'{menu_item.name} added to wishlist'
    
    return JsonResponse({
        'success': True,
        'is_wishlisted': is_wishlisted,
        'message': message
    })


@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('menu_item')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'cafe/wishlist.html', context)


@login_required
@require_POST
def rate_item(request):
    """Rate a menu item"""
    menu_item_id = request.POST.get('menu_item_id')
    rating_value = request.POST.get('rating')
    
    try:
        menu_item = MenuItem.objects.get(id=menu_item_id)
        rating_value = int(rating_value)
        
        if not (1 <= rating_value <= 5):
            return JsonResponse({'success': False, 'message': 'Invalid rating value'})
        
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            menu_item=menu_item,
            defaults={'rating': rating_value}
        )
        
        # Calculate new average rating
        avg_rating = menu_item.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        
        return JsonResponse({
            'success': True,
            'message': 'Rating updated successfully',
            'average_rating': round(avg_rating, 1),
            'user_rating': rating_value
        })
        
    except (MenuItem.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
@require_POST
def submit_review(request):
    """Submit a review for a menu item from an order"""
    menu_item_id = request.POST.get('menu_item_id')
    order_id = request.POST.get('order_id')
    rating_value = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()
    
    try:
        menu_item = MenuItem.objects.get(id=menu_item_id)
        order = Order.objects.get(id=order_id, user=request.user)
        rating_value = int(rating_value)
        
        # Validate rating
        if not (1 <= rating_value <= 5):
            return JsonResponse({'success': False, 'message': 'Invalid rating value'})
        
        # Check if order contains this item
        if not order.items.filter(menu_item=menu_item).exists():
            return JsonResponse({'success': False, 'message': 'This item is not in your order'})
        
        # Check if order is delivered
        if order.status != 'delivered':
            return JsonResponse({'success': False, 'message': 'You can only review delivered orders'})
        
        # Create or update review
        review, created = Review.objects.update_or_create(
            user=request.user,
            menu_item=menu_item,
            order=order,
            defaults={
                'rating': rating_value,
                'comment': comment
            }
        )
        
        # Also update or create rating
        Rating.objects.update_or_create(
            user=request.user,
            menu_item=menu_item,
            defaults={'rating': rating_value}
        )
        
        # Create notification for admin
        admin_users = User.objects.filter(is_staff=True, is_superuser=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title='New Review Submitted',
                message=f'{request.user.username} reviewed {menu_item.name} with {rating_value} stars',
                notification_type='info'
            )
        
        action = 'updated' if not created else 'submitted'
        return JsonResponse({
            'success': True,
            'message': f'Review {action} successfully! Thank you for your feedback.'
        })
        
    except (MenuItem.DoesNotExist, Order.DoesNotExist, ValueError) as e:
        return JsonResponse({'success': False, 'message': 'Invalid request'})


@require_POST
def apply_coupon(request):
    """Apply coupon to order or validate coupon"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login to apply coupon'})
    
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    validate_only = request.POST.get('validate_only', 'false').lower() == 'true'
    
    if not coupon_code:
        return JsonResponse({'success': False, 'message': 'Please enter a coupon code'})
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        
        # Check if coupon is valid
        if not coupon.is_valid:
            from django.utils import timezone
            now = timezone.now()
            
            if not coupon.is_active:
                return JsonResponse({'success': False, 'message': 'This coupon is no longer active'})
            elif now < coupon.valid_from:
                return JsonResponse({'success': False, 'message': 'This coupon is not yet valid'})
            elif now > coupon.valid_until:
                return JsonResponse({'success': False, 'message': 'This coupon has expired'})
            elif coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                return JsonResponse({'success': False, 'message': 'This coupon has reached its usage limit'})
            else:
                return JsonResponse({'success': False, 'message': 'Coupon is not valid'})
        
        # Calculate cart total
        cart_items = Cart.objects.filter(user=request.user, is_selected=True, saved_for_later=False)
        
        if not cart_items.exists():
            return JsonResponse({'success': False, 'message': 'Your cart is empty'})
        
        cart_total = sum(item.total_price for item in cart_items)
        
        if cart_total < coupon.minimum_order_amount:
            return JsonResponse({
                'success': False, 
                'message': f'Minimum order amount is ₹{coupon.minimum_order_amount}. Your cart total is ₹{cart_total}'
            })
        
        discount_amount = coupon.calculate_discount(cart_total)
        
        # If validation only, return success without applying
        if validate_only:
            return JsonResponse({
                'success': True,
                'message': f'✓ Valid! {coupon.description} - Save ₹{float(discount_amount)}',
                'discount_amount': float(discount_amount),
                'new_total': float(cart_total - discount_amount)
            })
        
        # Store coupon in session (actual application)
        request.session['applied_coupon'] = {
            'code': coupon.code,
            'discount_amount': float(discount_amount),
            'description': coupon.description
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Coupon {coupon.code} applied successfully!',
            'discount_amount': float(discount_amount),
            'new_total': float(cart_total - discount_amount)
        })
        
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error applying coupon: {str(e)}')
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


@login_required
def notifications_view(request):
    """Display user notifications"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark notifications as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'cafe/notifications.html', context)


@login_required
def remove_notification(request, notification_id):
    """Remove a specific notification"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            messages.success(request, 'Notification removed successfully.')
        except Notification.DoesNotExist:
            messages.error(request, 'Notification not found.')
    
    return redirect('notifications')


@login_required
def clear_all_notifications(request):
    """Clear all notifications for the current user"""
    if request.method == 'POST':
        count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, f'All {count} notifications cleared successfully.')
    
    return redirect('notifications')


@login_required
def delivery_addresses_view(request):
    """Manage delivery addresses"""
    addresses = DeliveryAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('delivery_addresses')
    else:
        form = DeliveryAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'cafe/delivery_addresses.html', context)


@login_required
@require_POST
def delete_address(request, address_id):
    """Delete a delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('delivery_addresses')


@login_required
def edit_address(request, address_id):
    """Edit a delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('delivery_addresses')
    else:
        form = DeliveryAddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
        'editing': True,
    }
    return render(request, 'cafe/edit_address.html', context)


@login_required
@require_POST
def set_default_address(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    # Remove default from all other addresses
    DeliveryAddress.objects.filter(user=request.user).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    messages.success(request, f'"{address.label}" set as default address!')
    return redirect('delivery_addresses')


def order_tracking_view(request, order_number):
    """Track order status"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Allow access to order owner or staff
    if request.user != order.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('orders')
    
    tracking_updates = OrderTracking.objects.filter(order=order)
    
    context = {
        'order': order,
        'tracking_updates': tracking_updates,
    }
    return render(request, 'cafe/order_tracking.html', context)


@login_required
def quick_reorder(request, order_number):
    """Quickly reorder items from a previous order"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Clear current cart
    Cart.objects.filter(user=request.user).delete()
    
    # Add items from the order to cart
    added_items = []
    unavailable_items = []
    
    for order_item in order.items.all():
        if order_item.menu_item.available:
            Cart.objects.create(
                user=request.user,
                menu_item=order_item.menu_item,
                quantity=order_item.quantity
            )
            added_items.append(order_item.menu_item.name)
        else:
            unavailable_items.append(order_item.menu_item.name)
    
    if added_items:
        messages.success(request, f'Added {len(added_items)} items to your cart!')
    
    if unavailable_items:
        messages.warning(request, f'Some items are no longer available: {", ".join(unavailable_items)}')
    
    return redirect('cart')


def menu_recommendations(request):
    """Get personalized menu recommendations"""
    if not request.user.is_authenticated:
        # For anonymous users, show popular items
        recommendations = MenuItem.objects.filter(
            available=True,
            is_featured=True
        )[:6]
    else:
        # For logged-in users, show personalized recommendations
        user_orders = Order.objects.filter(user=request.user)
        user_categories = set()
        
        for order in user_orders:
            for item in order.items.all():
                user_categories.add(item.menu_item.category)
        
        if user_categories:
            recommendations = MenuItem.objects.filter(
                available=True,
                category__in=user_categories
            ).exclude(
                id__in=Cart.objects.filter(user=request.user).values_list('menu_item_id', flat=True)
            )[:6]
        else:
            recommendations = MenuItem.objects.filter(
                available=True,
                is_featured=True
            )[:6]
    
    return JsonResponse({
        'recommendations': [{
            'id': item.id,
            'name': item.name,
            'price': str(item.discounted_price),
            'image': item.get_image_url,
            'url': item.get_absolute_url(),
            'rating': item.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        } for item in recommendations]
    })


# New Feature Views

@login_required
@require_POST
def save_for_later(request):
    """Move cart item to saved for later"""
    cart_item_id = request.POST.get('cart_item_id')
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.saved_for_later = True
    cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{cart_item.menu_item.name} saved for later'
    })


@login_required
@require_POST
def move_to_cart(request):
    """Move saved item back to cart"""
    cart_item_id = request.POST.get('cart_item_id')
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.saved_for_later = False
    cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{cart_item.menu_item.name} moved to cart'
    })


def quick_view_item(request, item_id):
    """Quick view modal endpoint for menu items"""
    item = get_object_or_404(MenuItem, id=item_id, available=True)
    avg_rating = item.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = item.reviews.count()
    
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': str(item.price),
        'discounted_price': str(item.discounted_price),
        'discount': str(item.discount),
        'has_discount': item.has_discount,
        'image': item.get_image_url,
        'category': item.category.name,
        'preparation_time': item.preparation_time,
        'ingredients': item.ingredients,
        'avg_rating': float(avg_rating),
        'review_count': review_count,
        'url': item.get_absolute_url(),
    })


def share_item(request, item_id):
    """Get shareable link for menu item"""
    item = get_object_or_404(MenuItem, id=item_id, available=True)
    share_url = request.build_absolute_uri(item.get_absolute_url())
    
    return JsonResponse({
        'url': share_url,
        'title': item.name,
        'description': item.description[:100] + '...' if len(item.description) > 100 else item.description,
        'image': item.get_image_url,
    })


@login_required
def print_receipt(request, order_number):
    """Print-friendly receipt view"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    
    return render(request, 'cafe/receipt.html', context)


# Real-time API endpoints
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def cart_count(request):
    """Get current cart item count"""
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user, is_selected=True).aggregate(
            total=Sum('quantity')
        )['total'] or 0
    else:
        # For anonymous users, get from session
        cart = request.session.get('cart', {})
        count = sum(item['quantity'] for item in cart.values())
    
    return JsonResponse({'count': count})

@require_http_methods(["POST"])
@login_required
def cart_add_ajax(request):
    """Add item to cart via AJAX"""
    import json
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    try:
        menu_item = MenuItem.objects.get(id=item_id, available=True)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menu_item=menu_item,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Item added to cart',
            'cart_count': Cart.objects.filter(user=request.user, is_selected=True).aggregate(
                total=Sum('quantity')
            )['total'] or 0
        })
    except MenuItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

@require_http_methods(["GET"])
def menu_search_ajax(request):
    """Live search for menu items"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    items = MenuItem.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        available=True
    )[:10]
    
    results = [{
        'id': item.id,
        'name': item.name,
        'slug': item.slug,
        'category': item.category.name,
        'price': str(item.discounted_price),
        'image': item.get_image_url  # Use the property that handles both image and image_url
    } for item in items]
    
    return JsonResponse({'results': results})

@require_http_methods(["GET"])
@login_required
def order_status_ajax(request, order_id):
    """Get order status for real-time tracking"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Calculate progress percentage
        status_progress = {
            'pending': 10,
            'confirmed': 30,
            'preparing': 50,
            'out_for_delivery': 75,
            'delivered': 100,
            'cancelled': 0
        }
        
        return JsonResponse({
            'status': order.status,
            'status_display': order.get_status_display(),
            'progress': status_progress.get(order.status, 0),
            'estimated_time': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@require_http_methods(["POST"])
@login_required
def wishlist_toggle_ajax(request):
    """Toggle wishlist item"""
    import json
    data = json.loads(request.body)
    item_id = data.get('item_id')
    
    try:
        menu_item = MenuItem.objects.get(id=item_id)
        wishlist_item = Wishlist.objects.filter(user=request.user, menu_item=menu_item).first()
        
        if wishlist_item:
            wishlist_item.delete()
            added = False
        else:
            Wishlist.objects.create(user=request.user, menu_item=menu_item)
            added = True
        
        return JsonResponse({
            'success': True,
            'added': added,
            'message': 'Added to wishlist' if added else 'Removed from wishlist'
        })
    except MenuItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

@require_http_methods(["GET"])
@login_required
def quick_view_ajax(request, item_id):
    """Get quick view HTML for menu item"""
    try:
        item = MenuItem.objects.get(id=item_id, available=True)
        
        html = f'''
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{item.name}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <img src="{item.image.url if item.image else '/static/images/default-food.jpg'}" 
                                 class="img-fluid rounded" alt="{item.name}">
                        </div>
                        <div class="col-md-6">
                            <span class="badge bg-primary mb-2">{item.category.name}</span>
                            <h4>{item.name}</h4>
                            <p class="text-muted">{item.description}</p>
                            <div class="mb-3">
                                <span class="h3 text-primary">₹{item.discounted_price}</span>
                                {f'<span class="text-muted text-decoration-line-through ms-2">₹{item.price}</span>' if item.discount > 0 else ''}
                            </div>
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary btn-lg" onclick="cartManager.addToCart({item.id}); bootstrap.Modal.getInstance(this.closest('.modal')).hide();">
                                    <i class="fas fa-cart-plus me-2"></i>Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return HttpResponse(html)
    except MenuItem.DoesNotExist:
        return HttpResponse('<div class="alert alert-danger">Item not found</div>', status=404)

@require_http_methods(["POST"])
@login_required
def cart_auto_save(request):
    """Auto-save cart for logged-in users"""
    import json
    data = json.loads(request.body)
    items = data.get('items', [])
    
    # Update cart items
    for item_data in items:
        try:
            cart_item = Cart.objects.get(
                user=request.user,
                menu_item_id=item_data['id']
            )
            cart_item.quantity = int(item_data['quantity'])
            cart_item.save()
        except Cart.DoesNotExist:
            pass
    
    return JsonResponse({'success': True})


# Advanced Features Endpoints
@require_http_methods(["GET"])
@login_required
def delivery_location_ajax(request, order_id):
    """Get real-time delivery location"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        tracking = OrderTracking.objects.filter(order=order).latest('created_at')
        
        # Simulate delivery location (in production, this would come from delivery partner API)
        return JsonResponse({
            'location': {
                'lat': 28.6139,  # Example coordinates
                'lng': 77.2090
            },
            'eta': '15 minutes',
            'status': tracking.status if tracking else order.status
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@require_http_methods(["POST"])
@login_required
def menu_recommendations_ajax(request):
    """Get personalized menu recommendations"""
    import json
    from django.db.models import Count, Q
    
    data = json.loads(request.body)
    viewed_items = data.get('viewedItems', [])
    
    # Get categories user has viewed
    viewed_categories = [item['category'] for item in viewed_items[-10:]]
    
    # Get popular items from those categories
    recommendations = MenuItem.objects.filter(
        category__name__in=viewed_categories,
        available=True
    ).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:8]
    
    # If not enough recommendations, add popular items
    if recommendations.count() < 4:
        popular_items = MenuItem.objects.filter(
            available=True
        ).annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:8]
        recommendations = popular_items
    
    results = [{
        'id': item.id,
        'name': item.name,
        'price': str(item.discounted_price),
        'image': item.image.url if item.image else '/static/images/default-food.jpg',
        'category': item.category.name
    } for item in recommendations]
    
    return JsonResponse({'recommendations': results})

@require_http_methods(["POST"])
@login_required
def cart_sync_ajax(request):
    """Sync offline cart data"""
    import json
    data = json.loads(request.body)
    
    # Process offline cart items
    for item in data.get('items', []):
        try:
            menu_item = MenuItem.objects.get(id=item['id'])
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                menu_item=menu_item,
                defaults={'quantity': item['quantity']}
            )
            if not created:
                cart_item.quantity = item['quantity']
                cart_item.save()
        except MenuItem.DoesNotExist:
            continue
    
    return JsonResponse({'success': True, 'message': 'Cart synced successfully'})

@require_http_methods(["POST"])
@login_required
def send_push_notification(request):
    """Send push notification to user"""
    import json
    data = json.loads(request.body)
    
    # Create notification in database
    Notification.objects.create(
        user=request.user,
        title=data.get('title'),
        message=data.get('message'),
        notification_type=data.get('type', 'info')
    )
    
    return JsonResponse({'success': True})


@login_required
def profile_view(request):
    """User profile view with edit functionality"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    # Get user statistics
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status__in=['pending', 'confirmed', 'preparing', 'out_for_delivery']).count()
    completed_orders = Order.objects.filter(user=request.user, status='delivered').count()
    cancelled_orders = Order.objects.filter(user=request.user, status='cancelled').count()
    
    total_spent = Order.objects.filter(user=request.user, status__in=['delivered', 'completed']).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    reviews_count = Review.objects.filter(user=request.user).count()
    addresses_count = DeliveryAddress.objects.filter(user=request.user).count()
    
    # Recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Favorite items (most ordered)
    favorite_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='delivered'
    ).values('menu_item__name', 'menu_item__id', 'menu_item__image', 'menu_item__image_url').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:3]
    
    # Recent reviews
    recent_reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    # Account age
    account_age = (timezone.now() - request.user.date_joined).days
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': total_spent,
        'wishlist_count': wishlist_count,
        'reviews_count': reviews_count,
        'addresses_count': addresses_count,
        'recent_orders': recent_orders,
        'favorite_items': favorite_items,
        'recent_reviews': recent_reviews,
        'account_age': account_age,
    }
    
    return render(request, 'cafe/profile.html', context)
