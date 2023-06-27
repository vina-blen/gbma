from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    return float(value) * float(arg)

@register.filter
def currency(value):
    return "₱ {:,.2f}".format(value)
