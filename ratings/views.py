from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from core.group_access import group_member_required
from songbook.models import Song

from .models import SongRating


def _score(value):
    """'' or '0' -> None (not rated); '1'..'5' -> int; anything else -> ValueError."""
    value = (value or "").strip()
    if value in ("", "0"):
        return None
    number = int(value)  # raises ValueError if it is not a whole number
    if not 1 <= number <= 5:
        raise ValueError("score out of range")
    return number


@group_member_required
@require_POST
def rate_song(request, group_slug, song_id):
    """Save (or clear) the logged-in member's rating and comment for one song."""
    song = get_object_or_404(Song, pk=song_id)
    try:
        stars = _score(request.POST.get("stars"))
        playability = _score(request.POST.get("playability"))
        singability = _score(request.POST.get("singability"))
    except ValueError:
        return HttpResponseBadRequest("Ratings must be whole numbers from 1 to 5.")
    comment = request.POST.get("comment", "").strip()[:500]

    if stars is None and playability is None and singability is None and not comment:
        # Everything blank means "remove my rating"
        SongRating.objects.filter(song=song, user=request.user).delete()
    else:
        SongRating.objects.update_or_create(
            song=song,
            user=request.user,
            defaults={
                "stars": stars,
                "playability": playability,
                "singability": singability,
                "comment": comment,
            },
        )
    return JsonResponse({"ok": True})


@group_member_required
def song_comments(request, group_slug, song_id):
    """The latest comments on one song, as JSON for the rating modal."""
    rows = (
        SongRating.objects.filter(song_id=song_id)
        .exclude(comment="")
        .select_related("user")
        .order_by("-updated")[:50]
    )
    return JsonResponse({
        "comments": [
            {
                "who": r.user.get_full_name() or r.user.get_username(),
                "stars": r.stars,
                "comment": r.comment,
                "when": r.updated.strftime("%b %d, %Y"),
            }
            for r in rows
        ]
    })
