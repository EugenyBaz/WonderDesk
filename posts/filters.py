from django import template

register = template.Library()


@register.filter(name="file_extension")
def file_extension(value):
    parts = value.split(".")
    if len(parts) > 1:
        return parts[-1].lower()
    return ""
