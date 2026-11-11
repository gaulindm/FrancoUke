# favorites/utils.py
"""
Helpers shared by the chord sheet view and the favorites views.

Who may see the numbers?
  - staff: hearts from every member of every club
  - a club leader (core.GroupMembership.role == "leader"): hearts from the
    members of the club(s) they lead
  - everybody else: only their own heart, never a count
"""
from django.urls import reverse

from core.models import Group, GroupMembership

from .models import SongFavorite


def led_groups(user):
    """The active clubs this user may see favorite counts for."""
    if not user.is_authenticated:
        return Group.objects.none()
    if user.is_staff:
        return Group.objects.filter(is_active=True)
    return Group.objects.filter(
        is_active=True,
        memberships__user=user,
        memberships__role="leader",
    ).distinct()


def favorite_count(song, groups):
    """How many different members of `groups` hearted `song`."""
    return (
        SongFavorite.objects
        .filter(song=song, user__group_memberships__group__in=groups)
        .values("user")
        .distinct()
        .count()
    )


def favorite_context(user, song):
    """
    Template context for the chord sheet. Anonymous visitors get nothing,
    which keeps the heart row hidden.
    """
    if not user.is_authenticated:
        return {}

    groups = led_groups(user)
    can_see_counts = groups.exists()

    context = {
        "favorite_toggle_url": reverse("favorites:toggle", args=[song.pk]),
        "is_favorite": SongFavorite.objects.filter(user=user, song=song).exists(),
        "can_see_favorite_counts": can_see_counts,
    }
    if can_see_counts:
        context["favorite_count"] = favorite_count(song, groups)
    return context