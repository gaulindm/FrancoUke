#setlist/views.py
import json
import logging
import re
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SetList, SetListSong
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
def setlist_list(request):
    setlists = SetList.objects.all().order_by("-created_at")
    return render(request, "setlists/setlist_list.html", {"setlists": setlists})


# ----------------------------
# 📄 Setlist detail view
# ----------------------------
def setlist_detail(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    songs = setlist.songs.select_related("song").order_by("order")

    # ✅ Group check
    can_edit = (
        request.user.is_authenticated
        and request.user.groups.filter(name="Leaders").exists()
    )

    # ✅ Event info (optional)
    event = setlist.event  # might be None

    # Performance group this setlist belongs to, if any (via its own
    # `group` field, or inherited from the linked event's group). Used
    # only so templates can build group-scoped board: links correctly.
    group = setlist.group or (event.group if event else None)

    return render(
        request,
        "setlists/detail.html",
        {
            "setlist": setlist,
            "songs": songs,
            "event": event,
            "can_edit": can_edit,
            "group": group,
        },
    )

def setlist_pdf(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
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
def setlist_teleprompter(request, setlist_id, order):
    """Teleprompter view for a song within a setlist."""
    setlist = get_object_or_404(SetList, pk=setlist_id)

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
            **context_data,
        },
    )

# ----------------------------
# 📦 Export / Import Setlists
# ----------------------------
def export_setlist(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
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


def import_setlist(request):
    if request.method == "POST" and request.FILES.get("setlist_file"):
        uploaded_file = request.FILES["setlist_file"]
        data = json.load(uploaded_file)

        new_setlist = SetList.objects.create(name="Imported Setlist")
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
        return redirect("setlists:detail", pk=new_setlist.pk)

    return render(request, "setlists/import_setlist.html")


# ----------------------------
# 🧱 Setlist Builder 
# ----------------------------
from django.db.models import Count, Prefetch
from board.models import SongRehearsalNote

@login_required
def setlist_builder(request, pk=None):
    """Create or edit a setlist via UI builder."""
    setlist = None
    if pk:
        setlist = get_object_or_404(SetList, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        if not setlist:
            setlist = SetList.objects.create(name=name, created_by=request.user)
        else:
            setlist.name = name
            setlist.save()

        # Clear old songs
        setlist.songs.all().delete()

        # Rebuild setlist order from POST data
        orders = request.POST.getlist("order[]")
        for idx, song_id in enumerate(orders, start=1):
            SetListSong.objects.create(
                setlist=setlist,
                song_id=song_id,
                order=idx,
            )

        return redirect("setlists:detail", pk=setlist.pk)

    # ✅ Prefetch rehearsal notes + their related rehearsal event titles
    songs = (
        Song.objects.all()
        .annotate(note_count=Count("rehearsal_notes"))
        .prefetch_related(
            Prefetch(
                "rehearsal_notes",
                queryset=SongRehearsalNote.objects.select_related("rehearsal__event"),
            )
        )
        .order_by("songTitle")
    )

    # Performance group this setlist belongs to, if any — same
    # inheritance rule as setlist_detail, for the same reason (templates
    # need it to build group-scoped board: links).
    group = None
    if setlist:
        group = setlist.group or (setlist.event.group if setlist.event else None)

    return render(
        request,
        "setlists/builder.html",
        {"setlist": setlist, "songs": songs, "group": group},
    )



# ----------------------------
# 🧱 AJAX filter for setlist builder
# ----------------------------

@login_required
def song_search(request):
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

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from board.models import Event
from .models import SetList

@login_required
@user_passes_test(lambda u: u.groups.filter(name="Leaders").exists())
def create_setlist_for_event(request, event_id):
    """Create a new setlist and link it to a specific event."""
    event = get_object_or_404(Event, pk=event_id)

    # Avoid duplicates
    if hasattr(event, "setlist") and event.setlist:
        return redirect("setlists:detail", pk=event.setlist.pk)

    setlist = SetList.objects.create(
        name=f"{event.title} Setlist",
        created_by=request.user,
        event=event,
        group=event.group,  # inherit the event's group, so this setlist is correctly tagged
    )

    return redirect("setlists:setlist_builder", pk=setlist.pk)