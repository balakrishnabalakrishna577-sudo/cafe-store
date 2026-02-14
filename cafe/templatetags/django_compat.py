from django import template

register = template.Library()

@register.filter
def length_is(value, arg):
    """
    Returns True if the value's length is the argument, or False otherwise.
    This filter was removed in Django 6.0 but is needed for compatibility.
    """
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False