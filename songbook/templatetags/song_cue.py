import json

from django import template
from django.utils.safestring import mark_safe

from songbook.utils.song_header import build_cue

register = template.Library()


@register.simple_tag
def cue_json(song):
    # Only digits and note letters get through build_cue, so this is safe to mark_safe.
    return mark_safe(json.dumps(build_cue(song)))   # "null" if no tempo or note