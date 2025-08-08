from django import template

register = template.Library()

@register.filter
def comma(value, decimals=1):
    try:
        return f"{float(value):.{decimals}f}".replace('.', ',')
    except (ValueError, TypeError):
        return ''