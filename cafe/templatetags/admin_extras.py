from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Return appropriate color class for order status"""
    colors = {
        'pending': 'warning',
        'confirmed': 'info',
        'preparing': 'primary',
        'ready': 'success',
        'out_for_delivery': 'info',
        'delivered': 'success',
        'cancelled': 'danger'
    }
    return colors.get(status, 'secondary')

@register.filter
def payment_status_color(status):
    """Return appropriate color class for payment status"""
    colors = {
        'pending': 'warning',
        'completed': 'success',
        'failed': 'danger',
        'refunded': 'info'
    }
    return colors.get(status, 'secondary')

@register.filter
def item_type_badge(item_type):
    """Return appropriate badge for item type"""
    if item_type == 'veg':
        return 'success'
    elif item_type == 'non-veg':
        return 'danger'
    return 'secondary'

@register.simple_tag
def calculate_percentage(value, total, max_value=100):
    """Calculate percentage for progress bars"""
    if total == 0:
        return 0
    percentage = (value / total) * max_value
    return min(percentage, max_value)

@register.filter
def currency_format(value):
    """Format currency values"""
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return f"${value}"

@register.filter
def order_status_icon(status):
    """Return appropriate icon for order status"""
    icons = {
        'pending': 'clock',
        'confirmed': 'check-circle',
        'preparing': 'utensils',
        'ready': 'box',
        'out_for_delivery': 'truck',
        'delivered': 'check-double',
        'cancelled': 'times-circle'
    }
    return icons.get(status, 'question-circle')