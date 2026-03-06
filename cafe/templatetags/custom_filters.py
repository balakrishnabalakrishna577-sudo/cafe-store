from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def status_color(status):
    """Return Bootstrap color class for order status"""
    status_colors = {
        'pending': 'warning',
        'confirmed': 'info',
        'preparing': 'primary',
        'out_for_delivery': 'info',
        'delivered': 'success',
        'cancelled': 'danger',
    }
    return status_colors.get(str(status), 'secondary')
