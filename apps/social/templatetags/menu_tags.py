from django.core.urlresolvers import reverse
from django import template

register = template.Library()


@register.simple_tag
def active(request, pattern):
    url = reverse(pattern)
    if (url == "/" and request.path == url) or (url != "/" and request.path.startswith(url)):
        return 'menu_curent'
    return ''