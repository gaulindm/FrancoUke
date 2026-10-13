# songbook/views/formatting_views.py

import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from songbook.context_processors import site_context
from songbook.forms import SongFormattingForm
from songbook.models import Song, SongFormatting


@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """
    Edit per-user SongFormatting.

    The first time a user formats a song, their formatting starts as a copy
    of someone else's: the song's contributor if they have one, otherwise
    the most recently created formatting by anyone else.
    """
    context_data = site_context(request)

    # Fetch the song first: a bad id now gives a 404 instead of a stray row
    song = get_object_or_404(Song, pk=song_id)

    # Ensure formatting exists for (user, song)
    formatting, created = SongFormatting.objects.get_or_create(
        user=request.user,
        song=song,
        defaults={
            "intro": {},
            "verse": {},
            "chorus": {},
            "bridge": {},
            "interlude": {},
            "outro": {},
            "centered": {},
        },
    )

    # First time this user formats this song: start from someone else's version
    if created:
        others = SongFormatting.objects.filter(song=song).exclude(user=request.user)
        source = (
            others.filter(user=song.contributor).first()
            or others.order_by("-pk").first()
        )
        if source:
            for section in ["intro", "verse", "chorus",
                            "bridge", "interlude", "outro"]:
                setattr(formatting, section, getattr(source, section))
            formatting.save()

    # Handle POST save
    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=formatting)
        if form.is_valid():
            form.save()
            messages.success(request, "Formatting updated successfully!")
            return redirect(f"{context_data['site_namespace']}:chord_sheet", pk=song.pk)
    else:
        form = SongFormattingForm(instance=formatting)

    return render(
        request,
        "songbook/edit_formatting.html",
        {
            "form": form,
            "pk": song.pk,
            "formatting": formatting,
            **context_data,
        },
    )