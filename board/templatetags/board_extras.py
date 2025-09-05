from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value from a dictionary for the given key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def cover_or_first(photos):
    return photos.filter(is_cover=True).first() or photos.first()
