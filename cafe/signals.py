from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Order, Notification, Coupon
from django.contrib.sessions.models import Session
from django.utils import timezone
import json


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
        except Exception:
            # Silently fail if there's an error creating the profile
            pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
    except Exception:
        # Silently fail if there's an error saving the profile
        pass


@receiver(pre_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    """Create notification when order status changes"""
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # Create notification for status change
                Notification.objects.create(
                    user=instance.user,
                    title=f'Order #{instance.order_number} Status Update',
                    message=f'Your order status has been updated to: {instance.get_status_display()}',
                    notification_type='order_update'
                )
        except (Order.DoesNotExist, Exception):
            # Silently fail if order doesn't exist or other error occurs
            pass


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    """Create notification when new order is created"""
    if created:
        try:
            # Create notification for new order
            Notification.objects.create(
                user=instance.user,
                title=f'Order #{instance.order_number} Placed',
                message=f'Your order has been placed successfully. Total: ${instance.grand_total}',
                notification_type='order_update'
            )
        except Exception:
            # Silently fail if notification creation fails
            pass


@receiver(post_delete, sender=Coupon)
def coupon_deleted(sender, instance, **kwargs):
    """Clear deleted coupon from all user sessions"""
    try:
        # Get all active sessions
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        
        for session in active_sessions:
            try:
                session_data = session.get_decoded()
                if 'applied_coupon' in session_data:
                    applied_coupon = session_data['applied_coupon']
                    # Check if the deleted coupon matches the session coupon
                    if applied_coupon.get('code') == instance.code:
                        # Remove the coupon from session
                        del session_data['applied_coupon']
                        session.session_data = session.encode(session_data)
                        session.save()
            except Exception:
                # Skip if there's an error decoding or updating session
                continue
    except Exception:
        # Silently fail if there's an error
        pass


@receiver(pre_save, sender=Coupon)
def coupon_deactivated(sender, instance, **kwargs):
    """Clear coupon from sessions when it's deactivated"""
    if instance.pk:  # Only for existing coupons
        try:
            old_coupon = Coupon.objects.get(pk=instance.pk)
            # If coupon is being deactivated
            if old_coupon.is_active and not instance.is_active:
                # Get all active sessions
                active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
                
                for session in active_sessions:
                    try:
                        session_data = session.get_decoded()
                        if 'applied_coupon' in session_data:
                            applied_coupon = session_data['applied_coupon']
                            # Check if the deactivated coupon matches the session coupon
                            if applied_coupon.get('code') == instance.code:
                                # Remove the coupon from session
                                del session_data['applied_coupon']
                                session.session_data = session.encode(session_data)
                                session.save()
                    except Exception:
                        # Skip if there's an error decoding or updating session
                        continue
        except (Coupon.DoesNotExist, Exception):
            # Silently fail if coupon doesn't exist or other error occurs
            pass