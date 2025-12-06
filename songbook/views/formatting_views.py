# songbook/views/formatting_views.py

import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from songbook.context_processors import site_context
from songbook.forms import SongFormattingForm
from songbook.models import SongFormatting


@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """
    Edit per-user SongFormatting with a dual-edit copy-from-Gaulind on first creation.
    """
    context_data = site_context(request)

    # Ensure formatting exists for (user, song)
    formatting, created = SongFormatting.objects.get_or_create(
        user=request.user,
        song_id=song_id,
        defaults={
            "intro": {},
            "verse": {},
            "chorus": {},
            "bridge": {},
            "interlude": {},
            "outro": {},
            "centered": {},  # ✔️ keep this
        },
    )

    # Auto-copy Gaulind formatting if this user just created their own
    if created:
        gaulind_formatting = SongFormatting.objects.filter(
            user__username="Gaulind",
            song_id=song_id
        ).first()

        if gaulind_formatting:
            for section in ["intro", "verse", "chorus",
                            "bridge", "interlude", "outro"]:
                setattr(formatting, section, getattr(gaulind_formatting, section))
            formatting.save()

    # Handle POST save
    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=formatting)
        if form.is_valid():
            form.save()
            messages.success(request, "Formatting updated successfully!")
            return redirect(f"{context_data['site_namespace']}:score_view", pk=song_id)
    else:
        form = SongFormattingForm(instance=formatting)

    return render(
        request,
        "songbook/edit_formatting.html",
        {
            "form": form,
            "pk": song_id,
            "formatting": formatting,
            **context_data,
        },
    )
