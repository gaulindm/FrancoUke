from django.shortcuts import render
from .models import Group


def landing_page(request):
    brands = [
        {
            "name": "FrancoUke",
            "desc": "Ton chansonnier francophone",
            "icon": "bi-music-note-beamed",
            "url": "francouke:home",
        },
        {
            "name": "StrumSphere",
            "desc": "Connect and strum around the world",
            "icon": "bi-globe",
            "url": "strumsphere:home",
        }
    ]

    # Top-level clubs only (parent__isnull=True excludes performance subgroups)
    clubs = list(Group.objects.filter(is_active=True, parent__isnull=True))

    member_group_ids = set()
    if request.user.is_authenticated:
        member_group_ids = set(
            request.user.group_memberships.values_list("group_id", flat=True)
        )

    for club in clubs:
        club.is_member = club.id in member_group_ids

    return render(request, "core/landing.html", {"brands": brands, "clubs": clubs})