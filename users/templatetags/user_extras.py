from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """
    Check if a user belongs to a specific group.
    Usage: {% if user|has_group:"Leaders" %}
    """
    return user.groups.filter(name=group_name).exists()
