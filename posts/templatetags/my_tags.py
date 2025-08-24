from django import template
from django.conf import settings

register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    else:
        return "#"