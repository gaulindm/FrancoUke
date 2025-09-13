from django.shortcuts import render, get_object_or_404
from songbook.models import Song
from songbook.utils.pdf_generator import load_relevant_chords, get_user_preferences
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html


def teleprompter_view(request, song_id):
    """
    Render the teleprompter view for a single song.
    """
    song = get_object_or_404(Song, pk=song_id)

    # Detect site (FrancoUke vs StrumSphere)
    site_name = "FrancoUke" if "franco" in request.get_host().lower() else "StrumSphere"

    # Prepare lyrics HTML for teleprompter
    lyrics_html = render_lyrics_with_chords_html(song.lyrics_with_chords, site_name)

    # Load user preferences for chords
    user_prefs = get_user_preferences(request.user)
    relevant_chords = load_relevant_chords([song], user_prefs, transpose_value=0)

    return render(request, "songbook/teleprompter.html", {
        "song": song,
        "lyrics_with_chords": lyrics_html,  # ✅ ready-to-use HTML
        "relevant_chords": relevant_chords,
        "site_name": site_name,
    })
