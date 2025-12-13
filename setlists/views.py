import json
import re
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SetList, SetListSong
from songbook.models import Song
from songbook.utils.chord_library import extract_relevant_chords
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html
from songbook.context_processors import site_context


# ----------------------------
# 🎨 Color Markup Helper
# ----------------------------
def apply_html_color_markup(text):
    """
    Convert custom color tags to HTML for web display.
    Similar to PDF apply_color_markup but outputs span tags.
    """
    if not text:
        return text
    
    color_map = {
        'red': 'red',
        'blue': 'blue',
        'green': 'green',
        'yellow': 'gold',
        'orange': 'orange',
        'pink': 'hotpink',
        'purple': 'purple',
    }
    
    # Full color names: <red>text</red> → <span style='color:red'>text</span>
    for tag, color in color_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<span style='color:{color}'>{m.group(1)}</span>", text)
    
    # Short color codes: <r>text</r> → <span style='color:red'>text</span>
    short_map = {'r': 'red', 'g': 'green', 'y': 'gold'}
    for tag, color in short_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<span style='color:{color}'>{m.group(1)}</span>", text)
    
    # Custom highlight: <highlight color="blue">text</highlight>
    pattern = re.compile(r'<highlight\s+color="(.*?)">(.*?)</highlight>', re.IGNORECASE | re.DOTALL)
    text = pattern.sub(lambda m: f"<span style='background-color:{m.group(1)}'>{m.group(2)}</span>", text)
    
    # Simple highlight: <h>text</h> → yellow background
    text = re.sub(r'<h>(.*?)</h>', r"<span style='background-color:yellow'>\1</span>", text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up any nested closing tags
    text = re.sub(r'</span>\s*</span>', '</span>', text)
    
    return text


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

    return render(
        request,
        "setlists/detail.html",
        {
            "setlist": setlist,
            "songs": songs,
            "event": event,
            "can_edit": can_edit,
        },
    )


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
        print(f"[TELEPROMPTER] suggested_alternate from metadata: {suggested_alternate}")

    # --- 🆕 Use load_relevant_chords (same as PDF) ---
    from songbook.utils.chords.loader import load_relevant_chords
    relevant_chords = load_relevant_chords(
        [current.song], 
        user_prefs, 
        transpose_value=0,
        suggested_alternate=suggested_alternate
    )

    # 🐛 DEBUG: Check what chords were loaded
    print(f"[TELEPROMPTER] Loaded {len(relevant_chords)} chord definitions")
    for chord in relevant_chords:
        print(f"  - {chord['name']}: {len(chord.get('variations', []))} variations")

    # --- Site context ---
    context_data = site_context(request)
    site_name = context_data["site_name"]

    # --- Render lyrics + metadata ---
    lyrics_html, metadata = render_lyrics_with_chords_html(
        current.song.lyrics_with_chords, site_name
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

    # --- User preferences for JS ---
    user_preferences = {
        "instrument": instrument,
        "isLefty": user_prefs["is_lefty"],
        "showAlternate": user_prefs["show_alternate_chords"],
    }

    # ----------------------------
    # 🐛 DEBUGGING OUTPUT
    # ----------------------------
    print("\n====== 🎶 TELEPROMPTER DEBUG ======")
    print(f"Setlist: {setlist.name} (ID {setlist.id})")
    print(f"Order: {current.order} / {total_songs}")
    print(f"Song: {current.song.songTitle} (ID {current.song.id})")
    print(f"Song.scroll_speed from DB: {getattr(current.song, 'scroll_speed', '❌ MISSING')}")
    print(f"Metadata scroll_speed (if any): {current.song.metadata.get('scroll_speed') if current.song.metadata else 'None'}")
    print(f"User: {request.user if request.user.is_authenticated else 'Anonymous'}")
    print(f"Relevant chords count: {len(relevant_chords)}")
    
    # 🎨 Check for color markup
    has_color_spans = '<span style=' in lyrics_html
    print(f"🎨 Color markup applied? {has_color_spans}")
    if has_color_spans:
        print("✅ Color spans detected in lyrics_html")
    else:
        print("⚠️ No color spans found - check if song has color tags")
    
    # ✅ Print metadata fields for debugging
    print(f"\n📋 Metadata fields available:")
    if metadata:
        for key, value in metadata.items():
            if value:
                print(f"  - {key}: {value}")
    print("==================================\n")

    # --- Use scroll speed from the Song model ---
    initial_scroll_speed = getattr(current.song, "scroll_speed", 40) or 40

    # 🐛 Confirm what we're actually passing to the template
    print(f"✅ Passing scroll speed to template: {initial_scroll_speed}\n")

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

    return render(
        request,
        "setlists/builder.html",
        {"setlist": setlist, "songs": songs},
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
        {"id": s.id, "title": s.songTitle}
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
    )

    return redirect("setlists:setlist_builder", pk=setlist.pk)