# songbook/views/misc_views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from songbook.models import Song
from songbook.context_processors import site_context


# ---------------------------------------------------------------------
# Static pages
# ---------------------------------------------------------------------

def about(request):
    return render(request, "songbook/about.html", site_context(request))


def whats_new(request):
    return render(request, "songbook/whats_new.html", site_context(request))


# ---------------------------------------------------------------------
# AJAX: Save scroll speed
# ---------------------------------------------------------------------

@csrf_exempt
def save_scroll_speed(request, song_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        new_speed = int(payload.get("scroll_speed", 20))
    except Exception:
        return JsonResponse({"error": "Invalid payload"}, status=400)

    try:
        song = Song.objects.get(pk=song_id)
        song.scroll_speed = new_speed
        song.save(update_fields=["scroll_speed"])
        return JsonResponse({"status": "ok", "scroll_speed": new_speed})
    except Song.DoesNotExist:
        return JsonResponse({"error": "Song not found"}, status=404)
