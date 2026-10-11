#setlist/views.py
import json
import logging
from django.db import transaction
from django.utils import timezone
import re
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.group_access import group_member_required, group_leader_required
from .models import SetList, SetListSong, SongSuggestion, SongSuggester
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from songbook.models import Song
from songbook.utils.chord_library import extract_relevant_chords
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html
from songbook.utils.chord_library import load_chord_dict
from songbook.utils.teleprompter_helpers import apply_html_color_markup, with_maj_aliases
from songbook.context_processors import site_context
from django.http import Http404
from django.utils.text import slugify
from .setlist_pdf import build_setlist_pdf

logger = logging.getLogger(__name__)


# ----------------------------
# 📋 List of all setlists
# ----------------------------
@group_member_required
def setlist_list(request, group_slug):
    group = request.group
    setlists = SetList.objects.filter(group=group).order_by("-created_at")
    pending_count = 0
    if request.is_group_leader:
        pending_count = SongSuggestion.objects.filter(
            group=group, status=SongSuggestion.Status.PENDING
        ).count()
    return render(request, "setlists/setlist_list.html",
                  {"setlists": setlists, "group": group, "pending_count": pending_count})

# ----------------------------
# 📄 Setlist detail view
# ----------------------------
@group_member_required
def setlist_detail(request, group_slug, pk):
    group = request.group
    setlist = get_object_or_404(SetList, pk=pk, group=group)
    songs = setlist.songs.select_related("song").order_by("order")

    return render(request, "setlists/detail.html", {
        "setlist": setlist,
        "songs": songs,
        "event": setlist.event,  # might be None
        "can_edit": request.is_group_leader,
        "group": group,
    })

@group_member_required
def setlist_pdf(request, group_slug, pk):
    setlist = get_object_or_404(SetList, pk=pk, group=request.group)
    if not setlist.songs.exists():
        raise Http404("This setlist has no songs.")

    site_name = site_context(request).get("site_name")
    user = request.user if request.user.is_authenticated else None
    large = request.GET.get("large") == "1"

    pdf_bytes = build_setlist_pdf(setlist, user=user, site_name=site_name,
                                  large_print=large)

    filename = (slugify(setlist.name) or f"setlist-{setlist.pk}") + ("-large-print" if large else "")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}.pdf"'
    return response





# ----------------------------
# 🎤 Teleprompter for a setlist song (WITH COLOR MARKUP)
# ----------------------------
@group_member_required
def setlist_teleprompter(request, group_slug, setlist_id, order):
    """Teleprompter view for a song within a setlist."""
    setlist = get_object_or_404(SetList, pk=setlist_id, group=request.group)
    
    # Ordered songs in the setlist
    songs = setlist.songs.select_related("song").order_by("order")
    total_songs = songs.count()

    # Find the current song in this setlist
    current = get_object_or_404(songs, setlist=setlist, order=order)

    # Find neighbors
    prev_song = songs.filter(order__lt=current.order).order_by("-order").first()
    next_song = songs.filter(order__gt=current.order).order_by("order").first()

    # --- Determine instrument ---
    instrument = request.GET.get("instrument")
    if not instrument and request.user.is_authenticated:
        instrument = getattr(request.user.userpreference, "primary_instrument", "ukulele")
    instrument = instrument or "ukulele"

    # --- 🆕 Get user preferences for chord loading ---
    user_pref = getattr(request.user, "userpreference", None)
    user_prefs = {
        "primary_instrument": instrument,
        "is_lefty": getattr(user_pref, "is_lefty", False),
        "show_alternate_chords": getattr(user_pref, "is_printing_alternate_chord", False),
        "use_known_chord_filter": False,  # Don't filter in teleprompter
        "known_chords": [],
    }

    # --- 🆕 Get suggested_alternate from song metadata ---
    suggested_alternate = None
    if current.song.metadata:
        suggested_alternate = current.song.metadata.get('suggested_alternate')
        logger.debug("suggested_alternate from metadata: %s", suggested_alternate)

    # --- 🆕 Use load_relevant_chords (same as PDF) ---
    from songbook.utils.chords.loader import load_relevant_chords
    relevant_chords = load_relevant_chords(
        [current.song], 
        user_prefs, 
        transpose_value=0,
        suggested_alternate=suggested_alternate
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Loaded %d chord definitions", len(relevant_chords))
        for chord in relevant_chords:
            logger.debug("  - %s: %d variations", chord["name"], len(chord.get("variations", [])))

    # --- Site context ---
    context_data = site_context(request)
    site_name = context_data["site_name"]

    # --- Render lyrics + metadata ---
    lyrics_html, metadata = render_lyrics_with_chords_html(
        current.song.lyrics_with_chords,
        site_name,
        chord_position="above",  # the page switches Above/Inline with CSS
    )

    # ✅ OVERRIDE with complete metadata from Song model
    # This ensures all metadata fields are available in the template
    if current.song.metadata:
        metadata = current.song.metadata
    
    # ✅ Check for slash chords in lyrics for the instruction message
    has_slash_chord = '/' in str(current.song.songChordPro)

    # ----------------------------
    # 🎨 Apply color markup transformations
    # ----------------------------
    lyrics_html = apply_html_color_markup(lyrics_html)

    # --- Full chord dictionary (lets transpose look up a real diagram) ---
    full_library = with_maj_aliases(load_chord_dict(instrument))

    # --- User preferences for JS ---
    user_preferences = {
        "instrument": instrument,
        "isLefty": user_prefs["is_lefty"],
        "showAlternate": user_prefs["show_alternate_chords"],
    }

    # ----------------------------
    # 🐛 DEBUG (only runs when the logger is set to DEBUG)
    # ----------------------------
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Setlist %s (%s) | song %d/%d: %s (ID %s) | user %s",
            setlist.name, setlist.id, current.order, total_songs,
            current.song.songTitle, current.song.id,
            request.user if request.user.is_authenticated else "Anonymous",
        )
        logger.debug("Song.scroll_speed: %s | chords: %d | color spans: %s",
                     getattr(current.song, "scroll_speed", "MISSING"),
                     len(relevant_chords), "<span style=" in lyrics_html)
        logger.debug("Metadata fields: %s",
                     {k: v for k, v in (metadata or {}).items() if v})

    # --- Use scroll speed from the Song model ---
    initial_scroll_speed = getattr(current.song, "scroll_speed", 40) or 40

    logger.debug("Passing scroll speed to template: %s", initial_scroll_speed)

    # --- Render template ---
    return render(
        request,
        "setlists/setlist_teleprompter.html",
        {
            "setlist": setlist,
            "song": current.song,
            "song_order": current.order,
            "total_songs": total_songs,
            "prev_song": prev_song,
            "next_song": next_song,
            "lyrics_with_chords": lyrics_html,
            "metadata": metadata,  # ✅ Now contains ALL fields from Song.metadata
            "has_slash_chord": has_slash_chord,  # ✅ New variable for template
            "relevant_chords_json": json.dumps(relevant_chords),
            "full_chord_library_json": json.dumps(full_library),
            "user_preferences_json": json.dumps(user_preferences),
            "initial_scroll_speed": initial_scroll_speed,
             "group": request.group,
            **context_data,
        },
    )

# ----------------------------
# 📦 Export / Import Setlists
# ----------------------------
@group_member_required
def export_setlist(request, group_slug, pk):
    setlist = get_object_or_404(SetList, pk=pk, group=request.group)
    data = {
        "setlist": [
            {
                "order": s.order,
                "title": s.song.songTitle,
                "lyrics": s.song.render_lyrics_with_chords_html(),
                "scroll_speed": getattr(s.song, "scroll_speed", 40),  # ✅ from Song
                "tempo": s.song.metadata.get("tempo") if s.song.metadata else None,
                "notes": s.rehearsal_notes,
            }
            for s in setlist.songs.all()
        ]
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename=\"setlist_{setlist.pk}.json\"'
    return response


@group_leader_required
def import_setlist(request, group_slug):
    group = request.group
    if request.method == "POST" and request.FILES.get("setlist_file"):
        uploaded_file = request.FILES["setlist_file"]
        data = json.load(uploaded_file)

        new_setlist = SetList.objects.create(
            name="Imported Setlist", group=group, created_by=request.user
        )
        for song_data in data["setlist"]:
            song, _ = Song.objects.get_or_create(
                songTitle=song_data["title"],
                defaults={
                    "songChordPro": song_data.get("lyrics", ""),
                    "scroll_speed": song_data.get("scroll_speed", 40),
                }
            )
            SetListSong.objects.create(
                setlist=new_setlist,
                song=song,
                order=song_data["order"],
                rehearsal_notes=song_data.get("notes", ""),
            )
        return redirect("setlists:detail", group_slug=group_slug, pk=new_setlist.pk)

    return render(request, "setlists/import_setlist.html", {"group": group})


# ----------------------------
# 🧱 Setlist Builder 
# ----------------------------
from django.db.models import Count, Prefetch, Q
from board.models import SongRehearsalNote

@group_leader_required
def setlist_builder(request, group_slug, pk=None):
    """Create or edit a setlist via UI builder."""
    group = request.group
    setlist = None
    if pk:
        setlist = get_object_or_404(SetList, pk=pk, group=group)

    if request.method == "POST":
        name = request.POST.get("name")
        if not setlist:
            setlist = SetList.objects.create(
                name=name, created_by=request.user, group=group
            )
        else:
            setlist.name = name
            setlist.save()

        setlist.songs.all().delete()

        orders = request.POST.getlist("order[]")
        for idx, song_id in enumerate(orders, start=1):
            SetListSong.objects.create(setlist=setlist, song_id=song_id, order=idx)

        return redirect("setlists:detail", group_slug=group_slug, pk=setlist.pk)

    # Songs are a shared pool, but rehearsal notes belong to a club,
    # so count and prefetch only THIS group's notes.
    songs = (
        Song.objects.all()
        .annotate(note_count=Count(
            "rehearsal_notes",
            filter=Q(rehearsal_notes__rehearsal__event__group=group),
        ))
        .prefetch_related(
            Prefetch(
                "rehearsal_notes",
                queryset=SongRehearsalNote.objects
                    .filter(rehearsal__event__group=group)
                    .select_related("rehearsal__event"),
            )
        )
        .order_by("songTitle")
    )

    return render(
        request,
        "setlists/builder.html",
        {"setlist": setlist, "songs": songs, "group": group},
    )
# ----------------------------
# 🧱 AJAX filter for setlist builder
# ----------------------------

@group_member_required
def song_search(request, group_slug):
    """AJAX endpoint to filter songs for the builder."""
    query = request.GET.get("q", "").strip().lower()
    songs = Song.objects.all()

    if query:
        songs = songs.filter(songTitle__icontains=query)

    results = [
        {"id": s.id, "title": s.songTitle, "origin": s.origin}
        for s in songs.order_by("songTitle")[:100]  # Limit to 100 results for speed
    ]

    return JsonResponse({"songs": results})

from board.models import Event

@group_leader_required
def create_setlist_for_event(request, group_slug, event_id):
    """Create a new setlist and link it to a specific event."""
    group = request.group
    event = get_object_or_404(Event, pk=event_id, group=group)

    if hasattr(event, "setlist") and event.setlist:
        return redirect("setlists:detail", group_slug=group_slug, pk=event.setlist.pk)

    setlist = SetList.objects.create(
        name=f"{event.title} Setlist",
        created_by=request.user,
        event=event,
        group=group,
    )

    return redirect("setlists:setlist_builder", group_slug=group_slug, pk=setlist.pk)

# ----------------------------
# 💡 Song suggestions (member side)
# ----------------------------
@group_member_required
@require_POST
def suggest_song(request, group_slug, song_id):
    """A club member suggests a song (one specific version) for this club."""
    group = request.group
    song = get_object_or_404(Song, pk=song_id, is_public=True)

    # site_name empty means the song is hidden from every platform
    if not song.site_name:
        raise Http404("This song is not available.")

    suggestion, created = SongSuggestion.objects.get_or_create(group=group, song=song)

    if suggestion.status == SongSuggestion.Status.APPROVED:
        messages.info(request, f"“{song.songTitle}” has already been approved for {group.name}.")
    elif suggestion.status == SongSuggestion.Status.DECLINED:
        reason = f" Leader's comment: {suggestion.leader_comment}" if suggestion.leader_comment else ""
        messages.info(request, f"“{song.songTitle}” was reviewed earlier and not added.{reason}")
    else:
        note = request.POST.get("note", "").strip()[:300]
        _, new_vote = SongSuggester.objects.get_or_create(
            suggestion=suggestion, user=request.user, defaults={"note": note}
        )
        if new_vote:
            messages.success(request, f"Thanks! “{song.songTitle}” was suggested for {group.name}. You can add a note under My suggestions.")
        else:
            messages.info(request, f"You already suggested “{song.songTitle}”.")

    # Go back to the page the member came from, if it is a safe address
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("setlists:my_suggestions", group_slug=group_slug)


@group_member_required
def my_suggestions(request, group_slug):
    """The songs this member has suggested for this club, and what happened to them."""
    group = request.group
    mine = (
        SongSuggester.objects
        .filter(user=request.user, suggestion__group=group)
        .select_related("suggestion__song", "suggestion__added_to_setlist")
        .order_by("-created_at")
    )
    return render(request, "setlists/my_suggestions.html", {
        "group": group,
        "my_suggestions": mine,
    })

@group_member_required
def suggest_song_search(request, group_slug):
    """AJAX: songs a member may suggest, each marked with where it stands for this club."""
    group = request.group
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"songs": []})

    # Same rule as suggest_song: public songs, and site_name set (empty = hidden)
    songs = list(
        Song.objects
        .filter(is_public=True, songTitle__icontains=query)
        .exclude(site_name__isnull=True)
        .exclude(site_name="")
        .order_by("songTitle")[:30]
    )

    existing = {
        s.song_id: s
        for s in SongSuggestion.objects.filter(group=group, song__in=songs)
    }
    mine = set(
        SongSuggester.objects
        .filter(user=request.user, suggestion__group=group, suggestion__song__in=songs)
        .values_list("suggestion__song_id", flat=True)
    )

    results = []
    for song in songs:
        suggestion = existing.get(song.id)
        if suggestion is None:
            state = "open"          # nobody has suggested this version yet
        elif suggestion.status == SongSuggestion.Status.APPROVED:
            state = "approved"
        elif suggestion.status == SongSuggestion.Status.DECLINED:
            state = "declined"
        elif song.id in mine:
            state = "mine"          # pending, and this member already suggested it
        else:
            state = "pending"       # pending, others suggested it; this member can add their name
        results.append({
            "id": song.id,
            "title": song.songTitle,
            "artist": (song.metadata or {}).get("artist") or "",
            "origin": song.origin,
            "state": state,
        })

    return JsonResponse({"songs": results})

@group_member_required
@require_POST
def edit_suggestion_note(request, group_slug, suggester_id):
    """A member changes the note on their own suggestion, while it is still pending."""
    suggester = get_object_or_404(
        SongSuggester.objects.select_related("suggestion__song"),
        pk=suggester_id,
        user=request.user,                 # only your own suggestions
        suggestion__group=request.group,   # and only in this club
    )

    if suggester.suggestion.status != SongSuggestion.Status.PENDING:
        messages.info(request, "A leader has already reviewed this suggestion, so its note can no longer be changed.")
    else:
        suggester.note = request.POST.get("note", "").strip()[:300]
        suggester.save(update_fields=["note"])
        messages.success(request, f"Your note on “{suggester.suggestion.song.songTitle}” was saved.")

    return redirect("setlists:my_suggestions", group_slug=group_slug)

# ----------------------------
# 💡 Song suggestions (leader side)
# ----------------------------
def _other_versions(group, song):
    """Other public, visible versions with the same title. The club's own version comes first."""
    if not song.songTitle:
        return []
    versions = list(
        Song.objects
        .filter(is_public=True, songTitle__iexact=song.songTitle)
        .exclude(pk=song.pk)
        .exclude(site_name__isnull=True)
        .exclude(site_name="")
    )
    own = group.origin_code
    versions.sort(key=lambda v: (not (own and v.origin == own), v.origin))
    return versions


@group_leader_required
def suggestion_queue(request, group_slug):
    """The leader's list of suggestions waiting for a decision."""
    group = request.group
    pending = list(
        SongSuggestion.objects
        .filter(group=group, status=SongSuggestion.Status.PENDING)
        .select_related("song")
        .prefetch_related("suggesters__user")
        .order_by("created_at")
    )
    for suggestion in pending:
        suggestion.other_versions = _other_versions(group, suggestion.song)

    reviewed = (
        SongSuggestion.objects
        .filter(group=group)
        .exclude(status=SongSuggestion.Status.PENDING)
        .select_related("song", "reviewed_by", "added_to_setlist")
        .order_by("-reviewed_at")[:15]
    )
    setlists = SetList.objects.filter(group=group).order_by("-created_at")

    return render(request, "setlists/suggestion_queue.html", {
        "group": group,
        "pending": pending,
        "reviewed": reviewed,
        "setlists": setlists,
    })


@group_leader_required
@require_POST
def review_suggestion(request, group_slug, pk):
    """Approve (add to a setlist) or decline one suggestion."""
    group = request.group
    suggestion = get_object_or_404(
        SongSuggestion.objects.select_related("song"), pk=pk, group=group
    )
    back = redirect("setlists:suggestion_queue", group_slug=group_slug)

    if suggestion.status != SongSuggestion.Status.PENDING:
        messages.info(request, "This suggestion has already been reviewed.")
        return back

    action = request.POST.get("action")
    comment = request.POST.get("leader_comment", "").strip()[:300]
    title = suggestion.song.songTitle

    if action == "decline":
        suggestion.status = SongSuggestion.Status.DECLINED
        suggestion.leader_comment = comment
        suggestion.reviewed_by = request.user
        suggestion.reviewed_at = timezone.now()
        suggestion.save()
        messages.success(request, f"“{title}” was declined.")
        return back

    if action != "approve":
        messages.error(request, "Please use the Approve or Decline button.")
        return back

    # --- Approve: which setlist? Must belong to this club.
    raw_setlist = request.POST.get("setlist_id", "")
    setlist = SetList.objects.filter(pk=raw_setlist, group=group).first() if raw_setlist.isdigit() else None
    if setlist is None:
        messages.error(request, "Please choose a setlist to add the song to.")
        return back

    # --- Which version? The one suggested, or another version of the same title.
    song_to_add = suggestion.song
    raw_song = request.POST.get("use_song_id", "")
    if raw_song.isdigit() and int(raw_song) != suggestion.song_id:
        allowed = {v.pk: v for v in _other_versions(group, suggestion.song)}
        song_to_add = allowed.get(int(raw_song))
        if song_to_add is None:
            messages.error(request, "That version of the song is not available.")
            return back
        note = f"Added the {song_to_add.origin or 'other'} version instead."
        comment = f"{comment} {note}".strip()[:300]

    with transaction.atomic():
        already_there = setlist.songs.filter(song=song_to_add).exists()
        if not already_there:
            # order=None lets SetListSong.save() put it at the end of the setlist
            SetListSong.objects.create(setlist=setlist, song=song_to_add, order=None)

        suggestion.status = SongSuggestion.Status.APPROVED
        suggestion.leader_comment = comment
        suggestion.reviewed_by = request.user
        suggestion.reviewed_at = timezone.now()
        suggestion.added_to_setlist = setlist
        suggestion.save()

    if already_there:
        messages.success(request, f"“{song_to_add.songTitle}” was already on {setlist.name}. Marked as approved.")
    else:
        messages.success(request, f"“{song_to_add.songTitle}” was added to {setlist.name}.")
    return back