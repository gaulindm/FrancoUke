# favorites/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from songbook.models import Song

from .models import SongFavorite
from .utils import favorite_count, led_groups


@login_required
@require_POST
def toggle_favorite(request, song_id):
    """Heart / un-heart a song. Returns {"is_favorite": bool, "count": int or null}."""
    song = get_object_or_404(Song, pk=song_id)

    # Same visibility rule as the rest of the songbook: only public songs,
    # or the member's own contributions.
    if not (song.is_public or song.contributor == request.user):
        raise Http404

    favorite, created = SongFavorite.objects.get_or_create(user=request.user, song=song)
    if not created:
        favorite.delete()          # second tap removes it

    groups = led_groups(request.user)
    return JsonResponse({
        "is_favorite": created,
        # Only leaders and staff ever receive a count.
        "count": favorite_count(song, groups) if groups.exists() else None,
    })


@login_required
def top_favorites(request):
    """
    Leaders' view for building the rotation setlists: songs ordered by how many
    members hearted them. Optional ?group=<slug> narrows it to one club.
    """
    groups = led_groups(request.user)
    if not groups.exists():
        raise Http404

    selected = None
    slug = request.GET.get("group")
    if slug:
        selected = get_object_or_404(groups, slug=slug)
    scope = [selected] if selected else groups

    songs = (
        Song.objects
        .filter(is_public=True, favorites__user__group_memberships__group__in=scope)
        .annotate(hearts=Count("favorites__user", distinct=True))
        .order_by("-hearts", "songTitle")
    )

    return render(request, "favorites/top_favorites.html", {
        "songs": songs,
        "groups": groups,
        "selected_group": selected,
    })