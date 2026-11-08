# <app>/templatetags/riff_tags.py   (put it next to user_tags.py)
from django import template

from songbook.utils.abc_riffs import has_riffs as _text_has_riffs

register = template.Library()


def _get(obj, name):
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


@register.filter
def has_riffs(items):
    """{% if songs|has_riffs %} ... {% endif %}

    True when any song in the setlist (a list of {"song": ...} items) has an ABC block.
    """
    for item in items or []:
        song = _get(item, "song")
        if song is not None and _text_has_riffs(_get(song, "songChordPro") or ""):
            return True
    return False