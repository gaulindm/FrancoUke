from django.shortcuts import render, get_object_or_404
from songbook.models import Song

def show(request, song_id):
    song = get_object_or_404(Song, pk=song_id)

    lyrics = song.songChordPro or ""   # your chordpro source
    title = song.songTitle or "Untitled Song"

    try:
        initial_transpose = int(request.GET.get("transpose", 0))
    except ValueError:
        initial_transpose = 0

    return render(request, "teleprompter/show.html", {
        "song_id": song.pk,
        "title": title,
        "lyrics": lyrics,
        "initial_transpose": initial_transpose,
    })
