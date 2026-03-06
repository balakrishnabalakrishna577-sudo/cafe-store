from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from cafe.models import Coupon


class NoCacheMiddleware(MiddlewareMixin):
    """
    Middleware to prevent browser caching of pages
    """
    
    def process_response(self, request, response):
        # Don't cache authenticated user pages
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


class CouponValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate applied coupons in session
    Removes invalid or deleted coupons automatically
    """
    
    def process_request(self, request):
        # Check if user has an applied coupon in session
        if 'applied_coupon' in request.session:
            applied_coupon = request.session['applied_coupon']
            coupon_code = applied_coupon.get('code')
            
            if coupon_code:
                try:
                    # Try to get the coupon from database
                    coupon = Coupon.objects.get(code=coupon_code)
                    
                    # Check if coupon is still valid
                    if not coupon.is_valid:
                        # Remove invalid coupon from session
                        del request.session['applied_coupon']
                        request.session.modified = True
                        
                        # Add a message for user if on cart/checkout page
                        if request.path in ['/cart/', '/checkout/']:
                            messages.warning(
                                request, 
                                f'Coupon {coupon_code} is no longer valid and has been removed.'
                            )
                except Coupon.DoesNotExist:
                    # Coupon was deleted, remove from session
                    del request.session['applied_coupon']
                    request.session.modified = True
                    
                    # Add a message for user if on cart/checkout page
                    if request.path in ['/cart/', '/checkout/']:
                        messages.warning(
                            request, 
                            f'Coupon {coupon_code} is no longer available and has been removed.'
                        )
        
        return None