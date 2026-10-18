from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

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


def _display_name(user):
    """What other members see next to a comment: first name, else the username
    (and never an email address, in case people register with one)."""
    name = user.first_name.strip() or user.get_username()
    return name.split("@")[0]


def _login_needed():
    # A clean 401 for the page's JavaScript (a redirect to the login page would
    # just come back as HTML that the script can't read).
    return JsonResponse({"error": "login required"}, status=401)


@require_POST
def rate_song(request, song_id):
    """Save (or clear) the logged-in user's rating and comment for one song."""
    if not request.user.is_authenticated:
        return _login_needed()
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


def song_comments(request, song_id):
    """The latest comments on one song, as JSON for the rating pop-up (logged-in users only)."""
    if not request.user.is_authenticated:
        return _login_needed()
    rows = (
        SongRating.objects.filter(song_id=song_id)
        .exclude(comment="")
        .select_related("user")
        .order_by("-updated")[:50]
    )
    return JsonResponse({
        "comments": [
            {
                "who": _display_name(r.user),
                "stars": r.stars,
                "comment": r.comment,
                "when": r.updated.strftime("%b %d, %Y"),
            }
            for r in rows
        ]
    })