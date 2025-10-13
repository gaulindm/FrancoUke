import json
import re
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SetList, SetListSong
from songbook.models import Song
from songbook.utils.chord_library import extract_relevant_chords
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html
from songbook.context_processors import site_context


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

    return render(
        request,
        "setlists/detail.html",
        {"setlist": setlist, "songs": songs},
    )


# ----------------------------
# 🎤 Teleprompter for a setlist song
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

    # --- Extract relevant chords ---
    relevant_chords = extract_relevant_chords(current.song.lyrics_with_chords, instrument)

    # --- Site context ---
    context_data = site_context(request)
    site_name = context_data["site_name"]

    # --- Render lyrics + metadata ---
    lyrics_html, metadata = render_lyrics_with_chords_html(
        current.song.lyrics_with_chords, site_name
    )

    # --- User preferences ---
    user_pref = getattr(request.user, "userpreference", None)
    user_preferences = {
        "instrument": getattr(user_pref, "primary_instrument", "ukulele"),
        "isLefty": getattr(user_pref, "is_lefty", False),
        "showAlternate": getattr(user_pref, "is_printing_alternate_chord", False),
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
    print("==================================\n")

    # --- Use scroll speed from the Song model ---
    initial_scroll_speed = getattr(current.song, "scroll_speed", 40) or 40

    # 🐛 Confirm what we’re actually passing to the template
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
            "metadata": metadata,
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
# 🧱 Setlist Builder (Admin tool)
# ----------------------------
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
        setlist.songs.clear()

        # Rebuild setlist order from POST data
        orders = request.POST.getlist("order[]")
        for idx, song_id in enumerate(orders, start=1):
            SetListSong.objects.create(
                setlist=setlist,
                song_id=song_id,
                order=idx,
                rehearsal_notes=request.POST.get(f"notes_{song_id}", ""),
            )

        return redirect("setlists:detail", pk=setlist.pk)

    songs = Song.objects.all().order_by("songTitle")
    return render(request, "setlists/builder.html", {
        "setlist": setlist,
        "songs": songs,
    })
