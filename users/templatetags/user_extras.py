from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """
    Check if a user belongs to a specific group.
    Usage: {% if user|has_group:"Leaders" %}
    """
    return user.groups.filter(name=group_name).exists()
import re
from urllib.parse import urlparse, parse_qs

@register.filter
def youtube_id(url):
    """Return the 11-character YouTube video ID from many URL formats, or ''."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    candidate = ""

    if host == "youtu.be":
        candidate = parsed.path.lstrip("/")
    elif host in ("youtube.com", "youtube-nocookie.com"):
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        else:
            parts = parsed.path.strip("/").split("/")
            if len(parts) > 1 and parts[0] in ("embed", "shorts", "live", "v"):
                candidate = parts[1]

    return candidate if re.fullmatch(r"[\w-]{11}", candidate) else ""