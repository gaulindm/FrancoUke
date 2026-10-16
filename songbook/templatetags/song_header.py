from django import template
from songbook.utils.song_header import build_song_header

register = template.Library()


@register.inclusion_tag("songbook/teleprompter/_song_header.html")
def song_header(song, show_strumming=True):
    """{% song_header song %} -> same header the PDF prints."""
    return {"h": build_song_header(song, show_strumming)}