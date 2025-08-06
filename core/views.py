from django.shortcuts import render


def landing_page(request):
    brands = [
        {
            "name": "FrancoUke",
            "desc": "Your local ukulele songbook",
            "icon": "bi-music-note-beamed",
            "url": "francouke:home",
        },
        {
            "name": "StrumSphere",
            "desc": "Connect and strum around the world",
            "icon": "bi-globe",
            "url": "strumsphere:home",
        },
        {
            "name": "Uke4ia Performers",
            "desc": "Manage your availability and plan carpools",
            "icon": "bi-people-fill",
            "url": "gigs:performer_gig_grid",  # 👈 Goes to new grid dashboard
        },
    ]
    return render(request, "core/landing.html", {"brands": brands})
