from django import template

from content.models import ContentBlock

register = template.Library()

@register.simple_tag
def get_content(slug):
    """
    Получает контент по заголовку
    """
    try:
        return ContentBlock.objects.get(slug=slug)

    except ContentBlock.DoesNotExist:
        return None
