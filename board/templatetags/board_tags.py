# board/templatetags/board_tags.py

from django import template

register = template.Library()

@register.filter
def availability_count(availabilities, status_code):
    return availabilities.filter(status=status_code).count()
