# board/views/rehearsal_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from board.models import Event, RehearsalDetails
from board.forms_rehearsal import RehearsalDetailsForm

# Optional helper: restrict to leaders only
def is_leader(user):
    return user.groups.filter(name="Leaders").exists()


@login_required
@user_passes_test(is_leader)
def edit_rehearsal_details(request, event_id):
    """View for leaders to create or edit rehearsal details (notes, focus, etc.)"""
    rehearsal_event = get_object_or_404(Event, pk=event_id, event_type="rehearsal")

    rehearsal_details, created = RehearsalDetails.objects.get_or_create(event=rehearsal_event)

    if request.method == "POST":
        form = RehearsalDetailsForm(request.POST, instance=rehearsal_details)
        if form.is_valid():
            form.save()
            # ✅ Redirect straight back to the main board — skip availability prompt
            return redirect("board:full_board")
    else:
        form = RehearsalDetailsForm(instance=rehearsal_details)

    return render(request, "board/edit_rehearsal_details.html", {
        "form": form,
        "rehearsal": rehearsal_event,
    })




@login_required
@user_passes_test(is_leader)
def edit_song_rehearsal_notes(request, event_id):
    """
    Edit individual song rehearsal notes linked to an event’s rehearsal.
    """
    event = get_object_or_404(Event, id=event_id)
    rehearsal_details, created = RehearsalDetails.objects.get_or_create(event=event)

    if request.method == "POST":
        formset = SongRehearsalNoteFormSet(request.POST, instance=rehearsal_details)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Song rehearsal notes updated successfully.")
            return redirect("board:rehearsal_detail", pk=event.id)
    else:
        formset = SongRehearsalNoteFormSet(instance=rehearsal_details)

    return render(
        request,
        "board/rehearsals/edit_song_rehearsal_notes.html",
        {"formset": formset, "event": event},
    )
