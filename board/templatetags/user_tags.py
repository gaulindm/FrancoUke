from django import template

register = template.Library()

@register.filter
def get_user_display_name(user):
    """
    Returns a friendly display name for a user.
    Falls back to username if no first/last name.
    """
    if not user:
        return "Unknown User"
    full_name = getattr(user, "get_full_name", lambda: "")()
    if full_name:
        return full_name
    first = getattr(user, "first_name", "")
    last = getattr(user, "last_name", "")
    if first or last:
        return f"{first} {last}".strip()
    return getattr(user, "username", "Unknown User")

