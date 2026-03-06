from django.db.models import Sum
from .models import Cart, Notification


def cart_count(request):
    """Add cart count to all templates"""
    try:
        if request.user.is_authenticated:
            count = Cart.objects.filter(user=request.user).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            return {'cart_count': count}
    except Exception:
        # Return 0 if there's any error (e.g., database not ready)
        pass
    return {'cart_count': 0}


def notifications_context(request):
    """Add notifications context to all templates"""
    try:
        if request.user.is_authenticated:
            unread_count = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
    except Exception:
        # Return 0 if there's any error (e.g., database not ready)
        pass
    return {'unread_notifications_count': 0}


def admin_session_context(request):
    """Add admin session context to admin templates"""
    if request.path.startswith('/admin/'):
        from django.contrib.auth.models import User
        from .models import UserProfile
        
        context = {
            'admin_user_id': request.session.get('admin_user_id'),
            'is_admin_session': request.session.get('is_admin_session', False),
            'admin_username': request.session.get('admin_username'),
            'admin_full_name': request.session.get('admin_full_name'),
            'admin_profile': None,
        }
        
        # Get admin profile if session exists
        if context['is_admin_session'] and context['admin_user_id']:
            try:
                admin_user = User.objects.get(id=context['admin_user_id'])
                profile, created = UserProfile.objects.get_or_create(user=admin_user)
                context['admin_profile'] = profile
            except (User.DoesNotExist, Exception):
                pass
        
        return context
    return {}



def advertisements_context(request):
    """Add active advertisements to all templates"""
    from .models import Advertisement
    try:
        # Get active advertisements for different positions
        ads = {
            'home_top_ads': Advertisement.objects.filter(
                is_active=True,
                position='home_top'
            ).order_by('display_order')[:2],
            
            'home_middle_ads': Advertisement.objects.filter(
                is_active=True,
                position='home_middle'
            ).order_by('display_order')[:4],
            
            'menu_sidebar_ads': Advertisement.objects.filter(
                is_active=True,
                position='menu_sidebar'
            ).order_by('display_order')[:2],
            
            'cart_bottom_ads': Advertisement.objects.filter(
                is_active=True,
                position='cart_bottom'
            ).order_by('display_order')[:2],
        }
        
        # Filter by date range
        for key in ads:
            ads[key] = [ad for ad in ads[key] if ad.is_currently_active]
        
        return {'advertisements': ads}
    except Exception:
        pass
    return {'advertisements': {}}
