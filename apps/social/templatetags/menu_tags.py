from django.core.urlresolvers import reverse
from django import template

register = template.Library()


@register.simple_tag
def active(request, pattern):
    if request.path.startswith(reverse(pattern)):
        return 'menu_curent'
    return ''