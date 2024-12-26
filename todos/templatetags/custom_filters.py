from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(value, css_class):
    return value.as_widget(attrs={'class': css_class})

@register.filter
def divideby(value, arg):
    try:
        return value / arg if arg != 0 else 0  # Prevent division by zero
    except (TypeError, ValueError):
        return 0 
    
@register.filter
def multiply(value, arg):
    try:
        return value * arg  # Multiply the values
    except (TypeError, ValueError):
        return 0  # Return 0 in case of invalid values
    
@register.filter
def addclass(value, arg):
    """Add class to a form field"""
    return value.as_widget(attrs={'class': arg}) if value else value