# songbook/views/pdf_views.py

import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from songbook.models import Song
from songbook.context_processors import site_context
from songbook.utils.pdf_generator import generate_songs_pdf
from songbook.utils.cal_pdf_generator import generate_songs_pdf as generate_cal_pdf  # chords above lyrics
from songbook.utils.transposer import transpose_lyrics
from django.utils.text import slugify
from songbook.utils.multi_song_pdf import build_songs_pdf


# -------------------------------------------------------------
# Which PDF layout? (picked on the chord sheet page: ?layout=cal)
# -------------------------------------------------------------
def chosen_layout(request):
    """Return 'cal' (chords above the lyrics) when the page asks for it, else 'standard'."""
    return "cal" if request.GET.get("layout") == "cal" else "standard"


# -------------------------------------------------------------
# Shared PDF helper
# -------------------------------------------------------------
def generate_pdf_response(
    filename,
    songs,
    user=None,
    transpose_value=0,
    formatting=None,
    site_name=None,
    inline=False,
    layout="standard",
):
    """
    Wrap PDF output in an HttpResponse and send it inline or as attachment.
    layout: "standard" (chords inline in the lyrics) or "cal" (chords above the lyrics).
    """
    content_type = "application/pdf"
    response = HttpResponse(content_type=content_type)

    disposition = "inline" if inline else "attachment"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}.pdf"'

    generate = generate_cal_pdf if layout == "cal" else generate_songs_pdf
    generate(
        response,
        songs,
        user=user,
        transpose_value=transpose_value,
        formatting=formatting,
        site_name=site_name,
    )

    return response


# -------------------------------------------------------------
# Multiple song PDF (tag filtered)
# -------------------------------------------------------------
MULTI_SONG_PDF_MAX = 50   # cap on songs per tag export; adjust after timing it

def generate_multi_song_pdf(request):
    """POST: {"tag_name": "...", optional "large": "1"} -> one PDF, one footer per song."""
    tag_name = request.POST.get("tag_name", "").strip()
    if not tag_name:
        return JsonResponse({"error": "Missing tag_name"}, status=400)

    songs = list(Song.objects.filter(tags__name=tag_name).distinct().order_by("songTitle"))
    if not songs:
        return JsonResponse({"error": f"No songs tagged '{tag_name}'"}, status=404)
    if len(songs) > MULTI_SONG_PDF_MAX:
        return JsonResponse(
            {"error": f"'{tag_name}' has {len(songs)} songs; the limit is {MULTI_SONG_PDF_MAX}."},
            status=400,
        )

    large = request.POST.get("large") == "1"
    site_name = site_context(request).get("site_name")
    user = request.user if request.user.is_authenticated else None

    n = len(songs)
    pdf_bytes = build_songs_pdf(
        songs,
        title=tag_name,
        subtitle_lines=[f"{n} song{'s' if n != 1 else ''}"],
        user=user,
        site_name=site_name,
        large_print=large,
    )

    filename = (slugify(tag_name) or "songs") + ("-large-print" if large else "")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response

# -------------------------------------------------------------
# Transposing helpers
# -------------------------------------------------------------
def _get_transpose(request):
    """Read ?transpose=N safely (0 if missing or not a number)."""
    try:
        return int(request.GET.get("transpose", "0") or 0)
    except ValueError:
        return 0


def _transposed_copy(song, steps):
    """
    Return an unsaved copy of the song with its chords transposed
    (the database is never touched). With steps == 0 the song itself is returned.
    """
    if not steps or not song.lyrics_with_chords:
        return song
    copy = Song(**{field.name: getattr(song, field.name) for field in song._meta.fields})
    copy.lyrics_with_chords = transpose_lyrics(song.lyrics_with_chords, steps)
    return copy


# -------------------------------------------------------------
# Single song PDF (inline)
# -------------------------------------------------------------
@login_required
def generate_single_song_pdf(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    steps = _get_transpose(request)
    site_name = site_context(request).get("site_name")

    return generate_pdf_response(
        filename=song.songTitle,
        songs=[_transposed_copy(song, steps)],
        user=request.user,
        transpose_value=0,   # lyrics are already transposed; don't transpose the footer twice
        formatting=None,
        site_name=site_name,
        inline=True,
        layout=chosen_layout(request),
    )


# -------------------------------------------------------------
# Preview PDF with optional transposing
# -------------------------------------------------------------
def preview_pdf(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    steps = _get_transpose(request)
    site_name = site_context(request).get("site_name")

    return generate_pdf_response(
        filename=f"{song.songTitle}_preview",
        songs=[_transposed_copy(song, steps)],
        user=request.user if request.user.is_authenticated else None,
        transpose_value=0,   # lyrics are already transposed; don't transpose the footer twice
        formatting=None,
        site_name=site_name,
        inline=True,
        layout=chosen_layout(request),
    )