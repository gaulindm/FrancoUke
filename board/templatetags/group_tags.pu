from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """Return True if user is in the given group."""
    return user.groups.filter(name=group_name).exists()
