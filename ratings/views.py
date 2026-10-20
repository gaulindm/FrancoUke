from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from songbook.mixins import SiteContextMixin
from songbook.models import Song

from .models import SongRating
from .utils import can_review_notes, face_icon


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
    """The private notes members left on one song, as JSON for the rating pop-up.

    Notes are for the song editors only: anyone else gets an empty list (they
    still see their OWN note, because their own rating fills the pop-up).
    """
    if not request.user.is_authenticated:
        return _login_needed()
    if not can_review_notes(request.user):
        return JsonResponse({"can_review": False, "comments": []})
    rows = (
        SongRating.objects.filter(song_id=song_id)
        .exclude(comment="")
        .select_related("user")
        .order_by("-updated")[:50]
    )
    return JsonResponse({
        "can_review": True,
        "comments": [
            {
                "id": r.pk,
                "who": _display_name(r.user),
                "stars": r.stars,
                "comment": r.comment,
                "when": r.updated.strftime("%b %d, %Y"),
            }
            for r in rows
        ]
    })


@require_POST
def delete_note(request, rating_id):
    """A song editor removes a member's note. The member's scores are kept."""
    if not request.user.is_authenticated:
        return _login_needed()
    if not can_review_notes(request.user):
        return JsonResponse({"error": "song editors only"}, status=403)
    rating = get_object_or_404(SongRating, pk=rating_id)
    rating.comment = ""
    if rating.stars is None and rating.playability is None and rating.singability is None:
        rating.delete()  # a note with no scores at all would leave an empty row behind
    else:
        rating.save(update_fields=["comment"])
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True})
    return redirect("ratings:notes_inbox")


class NotesInboxView(SiteContextMixin, TemplateView):
    """One page listing the latest member notes across all songs (song editors only)."""
    template_name = "ratings/notes_inbox.html"
    MAX_NOTES = 100

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not can_review_notes(request.user):
            return HttpResponseForbidden("Only the song editors can read member notes.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = (
            SongRating.objects.exclude(comment="")
            .select_related("song", "user")
            .order_by("-updated")[: self.MAX_NOTES]
        )
        context["notes"] = [
            {
                "id": r.pk,
                "song": r.song,
                "who": _display_name(r.user),
                "face": face_icon(r.stars),
                "comment": r.comment,
                "updated": r.updated,
            }
            for r in rows
        ]
        return context