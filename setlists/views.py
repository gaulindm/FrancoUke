import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import SetList, SetListSong
from songbook.models import Song

def setlist_list(request):
    setlists = SetList.objects.all().order_by("-created_at")
    return render(request, "setlists/setlist_list.html", {"setlists": setlists})

from django.shortcuts import render, get_object_or_404
from .models import SetList

def setlist_detail(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    songs = setlist.songs.select_related("song").order_by("order")

    return render(
        request,
        "setlists/detail.html",
        {"setlist": setlist, "songs": songs},
    )


from django.shortcuts import get_object_or_404, render
from .models import SetList, SetListSong

def setlist_teleprompter(request, setlist_id, order):
    """Teleprompter view for a song within a setlist."""
    setlist = get_object_or_404(SetList, pk=setlist_id)

    # Find the current song in this setlist
    current = get_object_or_404(
        SetListSong.objects.select_related("song"),
        setlist=setlist,
        order=order,
    )

    # Find neighbors
    prev_song = (
        setlist.songs.filter(order__lt=current.order).order_by("-order").first()
    )
    next_song = (
        setlist.songs.filter(order__gt=current.order).order_by("order").first()
    )

    return render(
        request,
        "setlists/setlist_teleprompter.html",
        {
            "setlist": setlist,
            "current": current,
            "prev_song": prev_song,
            "next_song": next_song,
        },
    )


def export_setlist(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    data = {
        "setlist": [
            {
                "order": s.order,
                "title": s.song.songTitle,
                "lyrics": s.song.render_lyrics_with_chords_html(),
                "scroll_speed": s.scroll_speed,
                "tempo": s.song.metadata.get("tempo") if s.song.metadata else None,
                "notes": s.rehearsal_notes,
            }
            for s in setlist.songs.all()
        ]
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="setlist_{setlist.pk}.json"'
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
                }
            )
            SetListSong.objects.create(
                setlist=new_setlist,
                song=song,
                order=song_data["order"],
                rehearsal_notes=song_data.get("notes", ""),
                scroll_speed=song_data.get("scroll_speed", 40),
            )
        return redirect("setlists:detail", pk=new_setlist.pk)

    return render(request, "setlists/import_setlist.html")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SetList, SetListSong
from songbook.models import Song

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
                scroll_speed=request.POST.get(f"scroll_{song_id}", 0),
            )

        return redirect("setlists:detail", pk=setlist.pk)

    songs = Song.objects.all().order_by("songTitle")
    return render(request, "setlists/builder.html", {
        "setlist": setlist,
        "songs": songs,
    })
