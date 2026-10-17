from django import template

from songbook.utils.song_header import extract_youtube_id, extract_youtube_start

register = template.Library()


@register.filter
def youtube_start(value):
    """Start offset in whole seconds taken from the stored link (0 if none)."""
    return extract_youtube_start(value)


@register.filter
def youtube_embed_url(value):
    """
    Turn whatever is stored in {youtube:...} into an embed address that
    keeps the start time.  Returns "" when there is no valid video.

        {% load youtube_tags %}
        {% with embed_url=song.metadata.youtube|youtube_embed_url %}
          {% if embed_url %}<iframe src="{{ embed_url }}" ...></iframe>{% endif %}
        {% endwith %}
    """
    video_id = extract_youtube_id(value)
    if not video_id:
        return ""
    url = f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"
    start = extract_youtube_start(value)
    if start:
        url += f"&start={start}"
    return url
