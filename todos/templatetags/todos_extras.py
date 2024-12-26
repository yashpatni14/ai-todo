from django import template

register = template.Library()

@register.filter
def addclass(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def divideby(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0