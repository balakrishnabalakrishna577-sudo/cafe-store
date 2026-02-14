from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json

from .models import Category, MenuItem, Order, OrderItem, UserProfile, Cart, Review, DeliveryAddress
from .forms import MenuItemForm, CategoryForm


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def is_admin_session(request):
    """Check if current session is an admin session"""
    if request.session.get('is_admin_session') and request.session.get('admin_user_id'):
        try:
            user = User.objects.get(id=request.session['admin_user_id'])
            return is_admin(user)
        except User.DoesNotExist:
            # Clear invalid session
            request.session.pop('admin_user_id', None)
            request.session.pop('is_admin_session', None)
            request.session.pop('admin_username', None)
            request.session.pop('admin_full_name', None)
            return False
    return False


def admin_required(view_func):
    """Decorator to require admin session"""
    def wrapper(request, *args, **kwargs):
        if not is_admin_session(request):
            messages.error(request, 'Please log in to access the admin panel.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_admin_user(request):
    """Get admin user from session"""
    if is_admin_session(request):
        try:
            return User.objects.get(id=request.session['admin_user_id'])
        except User.DoesNotExist:
            return None
    return None


def get_admin_context(request):
    """Get common admin context variables"""
    return {
        'admin_username': request.session.get('admin_username', ''),
        'admin_full_name': request.session.get('admin_full_name', ''),
    }


def admin_login_view(request):
    """Custom admin login with session separation"""
    # Check if admin is already logged in via admin session
    if request.session.get('admin_user_id') and request.session.get('is_admin_session'):
        try:
            user = User.objects.get(id=request.session['admin_user_id'])
            if is_admin(user):
                return redirect('custom_admin_dashboard')
        except User.DoesNotExist:
            # Clear invalid session
            request.session.pop('admin_user_id', None)
            request.session.pop('is_admin_session', None)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and is_admin(user):
            # Set admin session without logging into user session
            request.session['admin_user_id'] = user.id
            request.session['is_admin_session'] = True
            request.session['admin_username'] = user.username
            request.session['admin_full_name'] = user.get_full_name() or user.username
            
            # Don't use Django's login() to avoid user session
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
    
    return render(request, 'custom_admin/login.html')


def admin_logout_view(request):
    """Custom admin logout - only clears admin session"""
    # Clear admin session data
    request.session.pop('admin_user_id', None)
    request.session.pop('is_admin_session', None)
    request.session.pop('admin_username', None)
    request.session.pop('admin_full_name', None)
    
    messages.success(request, 'You have been logged out of the admin panel.')
    return redirect('admin_login')


@admin_required
def admin_dashboard(request):
    """Custom admin dashboard"""
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
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/dashboard.html', context)

    
@admin_required
def admin_orders(request):
    """Orders management"""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    payment_status_filter = request.GET.get('payment_status', '')
    date_filter = request.GET.get('date_filter', '')
    per_page = request.GET.get('per_page', '20')
    
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    # Date filtering
    if date_filter:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if date_filter == 'today':
            orders = orders.filter(created_at__date=today)
        elif date_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            orders = orders.filter(created_at__date=yesterday)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            orders = orders.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            orders = orders.filter(created_at__date__gte=month_ago)
    
    # Pagination
    if per_page == 'all':
        # Show all orders on one page
        paginated_orders = orders
        is_paginated = False
    else:
        try:
            per_page_int = int(per_page)
            if per_page_int > 100:  # Limit to prevent performance issues
                per_page_int = 100
        except (ValueError, TypeError):
            per_page_int = 20
        
        paginator = Paginator(orders, per_page_int)
        page_number = request.GET.get('page')
        paginated_orders = paginator.get_page(page_number)
        is_paginated = True
    
    # Statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    completed_orders = orders.filter(status='delivered').count()
    total_revenue = orders.filter(payment_status='completed').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    context = {
        'orders': paginated_orders,
        'status_filter': status_filter,
        'payment_status_filter': payment_status_filter,
        'date_filter': date_filter,
        'search': search,
        'per_page': per_page,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'is_paginated': is_paginated,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/orders.html', context)


@admin_required
def admin_order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order).select_related('menu_item')
    
    context = {
        'order': order,
        'order_items': order_items,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/order_detail.html', context)


@admin_required
@require_POST
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES):
        old_status = order.get_status_display()
        order.status = new_status
        order.save()
        messages.success(request, f'Order #{order.order_number} status updated from "{old_status}" to "{order.get_status_display()}" successfully!')
    else:
        messages.error(request, 'Invalid status selected.')
    
    return redirect('admin_order_detail', order_id=order_id)


@admin_required
@require_POST
def update_payment_method(request, order_id):
    """Update order payment method"""
    order = get_object_or_404(Order, id=order_id)
    new_payment_method = request.POST.get('payment_method')
    
    if new_payment_method in dict(Order.PAYMENT_METHOD_CHOICES):
        old_method = order.get_payment_method_display()
        order.payment_method = new_payment_method
        order.save()
        messages.success(request, f'Order #{order.order_number} payment method updated from "{old_method}" to "{order.get_payment_method_display()}" successfully!')
    else:
        messages.error(request, 'Invalid payment method selected.')
    
    return redirect('admin_order_detail', order_id=order_id)


@admin_required
@require_POST
def update_payment_status(request, order_id):
    """Update order payment status"""
    order = get_object_or_404(Order, id=order_id)
    new_payment_status = request.POST.get('payment_status')
    
    if new_payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
        old_status = order.get_payment_status_display()
        order.payment_status = new_payment_status
        
        # If marking as completed/paid, also update order status if needed
        if new_payment_status == 'completed' and order.status == 'pending':
            order.status = 'confirmed'
        
        order.save()
        
        # Create notification for customer about payment status change
        from .models import Notification
        if new_payment_status == 'completed':
            Notification.objects.create(
                user=order.user,
                title='Payment Confirmed!',
                message=f'Payment for order #{order.order_number} has been confirmed. Your order is now being processed.',
                notification_type='order_update'
            )
        elif new_payment_status == 'failed':
            Notification.objects.create(
                user=order.user,
                title='Payment Issue',
                message=f'There was an issue with payment for order #{order.order_number}. Please contact support or try again.',
                notification_type='order_update'
            )
        
        messages.success(request, f'Order #{order.order_number} payment status updated from "{old_status}" to "{order.get_payment_status_display()}" successfully!')
    else:
        messages.error(request, 'Invalid payment status selected.')
    
    return redirect('admin_order_detail', order_id=order_id)


@admin_required
@require_POST
def mark_payment_received(request, order_id):
    """Mark payment as received (for COD orders)"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.payment_method == 'cod':
        order.payment_status = 'completed'
        
        # Also update order status if it's still pending
        if order.status == 'pending':
            order.status = 'confirmed'
        
        order.save()
        
        # Create notification for customer
        from .models import Notification
        Notification.objects.create(
            user=order.user,
            title='Payment Received!',
            message=f'Cash payment for order #{order.order_number} has been received. Thank you!',
            notification_type='order_update'
        )
        
        messages.success(request, f'Cash payment for order #{order.order_number} marked as received!')
    else:
        messages.error(request, 'This action is only available for Cash on Delivery orders.')
    
    return redirect('admin_order_detail', order_id=order_id)


@admin_required
@require_POST
def mark_order_received(request, order_id):
    """Mark order as received/delivered"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'delivered':
        order.status = 'delivered'
        order.payment_status = 'completed'
        order.save()
        
        # Create notification for customer
        from .models import Notification
        Notification.objects.create(
            user=order.user,
            title='Order Delivered Successfully!',
            message=f'Your order #{order.order_number} has been delivered successfully. Thank you for choosing Spices of India Cuisine!',
            notification_type='order_update'
        )
        
        messages.success(request, f'Order #{order.order_number} marked as delivered and payment completed!')
    else:
        messages.info(request, f'Order #{order.order_number} is already marked as delivered.')
    
    return redirect('admin_order_detail', order_id=order_id)


@admin_required
@require_POST
def admin_cancel_order(request, order_id):
    """Admin manually cancels an order"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'delivered':
        messages.error(request, 'Cannot cancel an order that has already been delivered.')
        return redirect('admin_order_detail', order_id=order_id)
        
    order.status = 'cancelled'
    if order.payment_status != 'completed':
        order.payment_status = 'failed'
    order.save()
    
    # Create notification for customer
    from .models import Notification
    Notification.objects.create(
        user=order.user,
        title='Order Cancelled by Admin',
        message=f'Your order #{order.order_number} has been cancelled by the cafe. Please contact us for more details.',
        notification_type='order_update'
    )
    
    messages.success(request, f'Order #{order.order_number} has been cancelled.')
    return redirect('admin_order_detail', order_id=order_id)


@admin_required
def admin_menu(request):
    """Menu management"""
    # Handle sample data creation
    if request.method == 'POST' and request.POST.get('action') == 'add_samples':
        from django.core.management import call_command
        try:
            call_command('add_sample_menu_with_images')
            messages.success(request, 'Sample menu items with images added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding sample items: {str(e)}')
        return redirect('admin_menu')
    
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    items = MenuItem.objects.select_related('category').order_by('category__name', 'name')
    
    if category_filter:
        items = items.filter(category_id=category_filter)
    
    if search:
        items = items.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    items = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'items': items,
        'categories': categories,
        'category_filter': category_filter,
        'search': search,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/menu.html', context)


@admin_required
def admin_menu_add(request):
    """Add menu item"""
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save()
            messages.success(request, f'Menu item "{menu_item.name}" added successfully!')
            return redirect('admin_menu')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MenuItemForm()
    
    categories = Category.objects.all()
    context = {
        'form': form, 
        'title': 'Add Menu Item',
        'categories': categories,
        **get_admin_context(request),
    }
    return render(request, 'custom_admin/menu_form.html', context)


@admin_required
def admin_menu_edit(request, item_id):
    """Edit menu item"""
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            menu_item = form.save()
            messages.success(request, f'Menu item "{menu_item.name}" updated successfully!')
            return redirect('admin_menu')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MenuItemForm(instance=item)
    
    categories = Category.objects.all()
    context = {
        'form': form, 
        'title': 'Edit Menu Item', 
        'item': item,
        'categories': categories,
        **get_admin_context(request),
    }
    return render(request, 'custom_admin/menu_form.html', context)


@admin_required
def admin_menu_delete(request, item_id):
    """Delete menu item"""
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Menu item "{item_name}" deleted successfully!')
        return redirect('admin_menu')
    
    return render(request, 'custom_admin/confirm_delete.html', {
        'item': item, 
        'type': 'Menu Item',
        **get_admin_context(request),
    })


@admin_required
def admin_categories(request):
    """Categories management"""
    categories = Category.objects.annotate(
        item_count=Count('items')
    ).order_by('name')
    
    context = {
        'categories': categories,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/categories.html', context)


@admin_required
def admin_category_add(request):
    """Add category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('admin_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    return render(request, 'custom_admin/category_form.html', {
        'form': form, 
        'title': 'Add Category',
        **get_admin_context(request),
    })


@admin_required
def admin_category_edit(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'custom_admin/category_form.html', {
        'form': form, 
        'title': 'Edit Category', 
        'category': category,
        **get_admin_context(request),
    })


@admin_required
def admin_category_delete(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('admin_categories')
    
    return render(request, 'custom_admin/confirm_delete.html', {
        'item': category, 
        'type': 'Category',
        **get_admin_context(request),
    })


@admin_required
def admin_customers(request):
    """Customers management"""
    search = request.GET.get('search', '')
    
    customers = UserProfile.objects.select_related('user').order_by('-user__date_joined')
    
    if search:
        customers = customers.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    customers_page = paginator.get_page(page_number)
    
    # Add order statistics only for current page
    for customer in customers_page:
        customer.order_count = Order.objects.filter(user=customer.user).count()
        customer.total_spent = Order.objects.filter(
            user=customer.user, 
            payment_status='completed'
        ).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'customers': customers_page,
        'search': search,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/customers.html', context)


@admin_required
def admin_customer_detail(request, customer_id):
    """Customer detail view"""
    customer = get_object_or_404(UserProfile, id=customer_id)
    
    # Get customer orders
    orders = Order.objects.filter(user=customer.user).order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    completed_orders = orders.filter(status='delivered').count()
    pending_orders = orders.filter(status__in=['pending', 'confirmed', 'preparing', 'ready']).count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    total_spent = orders.filter(payment_status='completed').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0
    
    # Get recent orders (last 10)
    recent_orders = orders[:10]
    
    # Get delivery addresses
    addresses = DeliveryAddress.objects.filter(user=customer.user).order_by('-is_default', '-created_at')
    
    context = {
        'customer': customer,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
        'recent_orders': recent_orders,
        'addresses': addresses,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/customer_detail.html', context)


@admin_required
def admin_reviews(request):
    """Reviews management"""
    from django.db.models import Q
    
    # Filters
    rating_filter = request.GET.get('rating', '')
    search = request.GET.get('search', '')
    
    reviews = Review.objects.select_related('user', 'menu_item', 'order').order_by('-created_at')
    
    # Apply filters
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    if search:
        reviews = reviews.filter(
            Q(user__username__icontains=search) |
            Q(menu_item__name__icontains=search) |
            Q(comment__icontains=search)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Rating distribution with percentages
    rating_distribution = []
    five_star_count = 0
    low_rating_count = 0
    
    for rating in [5, 4, 3, 2, 1]:
        count = Review.objects.filter(rating=rating).count()
        percentage = (count * 100 / total_reviews) if total_reviews > 0 else 0
        rating_distribution.append({
            'rating': rating,
            'count': count,
            'percentage': round(percentage, 1)
        })
        
        if rating == 5:
            five_star_count = count
        elif rating in [1, 2]:
            low_rating_count += count
    
    context = {
        'page_obj': page_obj,
        'reviews': page_obj.object_list,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'five_star_count': five_star_count,
        'low_rating_count': low_rating_count,
        'rating_filter': rating_filter,
        'search': search,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/reviews.html', context)


@admin_required
@require_POST
def admin_delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id)
    menu_item_name = review.menu_item.name
    user_name = review.user.username
    
    review.delete()
    
    messages.success(request, f'Review by {user_name} for {menu_item_name} has been deleted.')
    return redirect('admin_reviews')


@admin_required
def admin_analytics(request):
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
        'daily_sales': json.dumps(daily_sales),
        'category_stats': category_stats,
        'current_month_revenue': current_month_revenue,
        'last_month_revenue': last_month_revenue,
        'growth_percentage': round(growth_percentage, 1),
        'top_items': top_items,
        'status_distribution': status_distribution,
        'total_revenue_30_days': sum(item['sales'] for item in daily_sales),
        'avg_daily_sales': sum(item['sales'] for item in daily_sales) / 30,
        **get_admin_context(request),
    }
    
    return render(request, 'custom_admin/analytics.html', context)


@admin_required
def admin_settings(request):
    """Admin settings page with profile update and password change functionality"""
    from django.contrib.auth.forms import PasswordChangeForm
    
    # Get admin user from session
    admin_user = get_admin_user(request)
    if not admin_user:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('admin_login')
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update profile information
            admin_user.email = request.POST.get('email', admin_user.email)
            admin_user.first_name = request.POST.get('first_name', admin_user.first_name)
            admin_user.last_name = request.POST.get('last_name', admin_user.last_name)
            
            # Handle profile image upload
            if 'profile_image' in request.FILES:
                profile.image = request.FILES['profile_image']
                profile.save()
            
            try:
                admin_user.save()
                # Update session data
                request.session['admin_full_name'] = admin_user.get_full_name() or admin_user.username
                messages.success(request, 'Profile updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
            
            return redirect('admin_settings')
        
        elif action == 'remove_image':
            # Remove profile image
            if profile.image and profile.image.name != 'default-user.png':
                profile.image.delete(save=False)
                profile.image = 'default-user.png'
                profile.save()
                messages.success(request, 'Profile image removed successfully!')
            return redirect('admin_settings')
        
        elif action == 'change_password':
            # Change password
            form = PasswordChangeForm(admin_user, request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'Password changed successfully!')
            else:
                # Display all form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == 'old_password':
                            messages.error(request, f'Current password: {error}')
                        elif field == 'new_password1':
                            messages.error(request, f'New password: {error}')
                        elif field == 'new_password2':
                            messages.error(request, f'Confirm password: {error}')
                        else:
                            messages.error(request, error)
            
            return redirect('admin_settings')
    
    # GET request
    password_form = PasswordChangeForm(admin_user)
    context = {
        'password_form': password_form,
        'user': admin_user,
        'profile': profile,
        **get_admin_context(request),
    }
    return render(request, 'custom_admin/settings.html', context)