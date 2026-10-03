# setlist/setlist_pdf.py
"""Printable PDF of a setlist. The real work is in songbook.utils.multi_song_pdf."""
from songbook.utils.multi_song_pdf import build_songs_pdf


def _subtitle_lines(setlist):
    lines = []
    event = getattr(setlist, "event", None)
    if event:
        if getattr(event, "event_date", None):
            lines.append(event.event_date.strftime("%A, %B %d, %Y"))
        if getattr(event, "location", ""):
            lines.append(str(event.location))
    return lines


def build_setlist_pdf(setlist, user=None, site_name=None,
                      contents_page=True, page_numbers=True, large_print=False):
    """PDF bytes for every song in `setlist`, in setlist order."""
    songs = [item.song for item in
             setlist.songs.select_related("song").order_by("order")]
    return build_songs_pdf(
        songs,
        title=setlist.name,
        subtitle_lines=_subtitle_lines(setlist),
        user=user,
        site_name=site_name,
        contents_page=contents_page,
        page_numbers=page_numbers,
        large_print=large_print,
    )