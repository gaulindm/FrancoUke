# board/views/rehearsal_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from board.models import Event, RehearsalDetails
from django.contrib import messages  # ✅ Add this

from board.forms_rehearsal import RehearsalDetailsForm, SongRehearsalNote
from board.rehearsal_notes import SongRehearsalNote
from songbook.models import Song
from core.group_access import group_member_required


# Optional helper: restrict to leaders only
def is_leader(user):
    return user.groups.filter(name="Leaders").exists()


@group_member_required
@user_passes_test(is_leader)
def edit_rehearsal_details(request, group_slug, event_id):
    """View for leaders to create or edit rehearsal details (notes, focus, etc.)"""
    group = request.group
    rehearsal_event = get_object_or_404(Event, pk=event_id, event_type="rehearsal", group=group)

    rehearsal_details, created = RehearsalDetails.objects.get_or_create(event=rehearsal_event)

    if request.method == "POST":
        form = RehearsalDetailsForm(request.POST, instance=rehearsal_details)
        if form.is_valid():
            form.save()
            # ✅ Redirect straight back to the main board — skip availability prompt
            return redirect("board:full_board", group_slug=group_slug)
    else:
        form = RehearsalDetailsForm(instance=rehearsal_details)

    return render(request, "board/edit_rehearsal_details.html", {
        "form": form,
        "rehearsal": rehearsal_event,
        "group": group,
    })


@group_member_required
def song_rehearsal_history(request, group_slug, song_id):
    """
    Display all rehearsal notes linked to a specific song, scoped to
    THIS group's rehearsals/events only (songs themselves aren't
    group-scoped — they're shared across the whole songbook — but the
    rehearsal notes attached to them are group-specific).
    """
    group = request.group
    song = get_object_or_404(Song, pk=song_id)

    notes = (
        SongRehearsalNote.objects
        .filter(song=song, rehearsal__event__group=group)
        .select_related("rehearsal__event", "created_by")
        .order_by("-rehearsal__event__event_date", "-created_at")
    )

    return render(request, "board/song_rehearsal_history.html", {
        "song": song,
        "notes": notes,
        "group": group,
    })


@group_member_required
@user_passes_test(is_leader)
def edit_song_rehearsal_notes(request, group_slug, event_id):
    group = request.group
    event = get_object_or_404(Event, id=event_id, group=group)
    rehearsal_details, _ = RehearsalDetails.objects.get_or_create(event=event)

    SongNote = SongRehearsalNote
    existing_notes = SongNote.objects.filter(rehearsal=rehearsal_details).select_related("song")

    if request.method == "POST":
        # Clear existing notes and rebuild from POST
        SongNote.objects.filter(rehearsal=rehearsal_details).delete()
        for key, value in request.POST.items():
            if key.startswith("notes_") and value.strip():
                song_id = key.split("_")[1]
                SongNote.objects.create(
                    rehearsal=rehearsal_details,
                    song_id=song_id,
                    notes=value.strip(),
                    created_by=request.user
                )
        messages.success(request, "🎶 Rehearsal song notes updated.")
        return redirect("board:full_board", group_slug=group_slug)

    songs = Song.objects.all().order_by("songTitle")
    return render(
        request,
        "board/edit_song_rehearsal_notes.html",
        {"event": event, "songs": songs, "notes": existing_notes, "group": group},
    )