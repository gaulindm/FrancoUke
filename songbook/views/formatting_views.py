# songbook/views/formatting_views.py

import copy
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from songbook.context_processors import site_context
from songbook.forms import SongFormattingForm
from songbook.models import Song, SongFormatting


FORMATTING_SECTIONS = ["intro", "verse", "chorus", "bridge", "interlude", "outro", "centered"]


def _requested_layout(request):
    """'cal' (chords above the lyrics) when asked for with ?layout=cal, else 'standard'."""
    value = request.POST.get("layout") or request.GET.get("layout")
    return "cal" if value == "cal" else "standard"


def _cal_form_target(formatting):
    """A throw-away copy of `formatting` for the form to edit in "cal" mode.

    Its section fields hold the CAL settings: the standard settings underneath,
    whatever is saved in formatting.cal on top. It is never saved itself.
    """
    target = copy.copy(formatting)
    cal = getattr(formatting, "cal", None) or {}
    for section in FORMATTING_SECTIONS:
        values = copy.deepcopy(getattr(formatting, section, None) or {})
        values.update(copy.deepcopy(cal.get(section) or {}))
        setattr(target, section, values)
    return target


def _save_cal_formatting(formatting, edited, sections):
    """Store what the form changed into formatting.cal.

    A section is stored only if it now differs from the standard formatting;
    sections left as they are keep following the standard formatting.
    """
    cal = dict(getattr(formatting, "cal", None) or {})
    for section in sections:
        values = getattr(edited, section) or {}
        if values != (getattr(formatting, section, None) or {}):
            cal[section] = values
        else:
            cal.pop(section, None)
    formatting.cal = cal
    formatting.save(update_fields=["cal"])


@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """
    Edit per-user SongFormatting.

    ?layout=cal edits the formatting used by the "chords above lyrics" PDF
    (saved in SongFormatting.cal); without it, the standard formatting.

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

    layout = _requested_layout(request)
    target = _cal_form_target(formatting) if layout == "cal" else formatting

    # Handle POST save
    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=target)
        if form.is_valid():
            if layout == "cal":
                edited = form.save(commit=False)
                _save_cal_formatting(
                    formatting, edited,
                    [name for name in FORMATTING_SECTIONS if name in form.fields],
                )
            else:
                form.save()
            messages.success(request, "Formatting updated successfully!")
            return redirect(f"{context_data['site_namespace']}:chord_sheet", pk=song.pk)
    else:
        form = SongFormattingForm(instance=target)

    return render(
        request,
        "songbook/edit_formatting.html",
        {
            "form": form,
            "pk": song.pk,
            "formatting": formatting,
            **context_data,
            "layout": layout,      # after **context_data so nothing in site_context can replace it
        },
    )