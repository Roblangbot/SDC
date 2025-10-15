from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    """Check if the string `value` starts with `arg`."""
    if isinstance(value, str):
        return value.startswith(arg)
    return False
