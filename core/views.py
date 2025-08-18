from django.shortcuts import render


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
        },
        {
            "name": "Uke4ia Performers",
            "desc": "Manage your availability and be informed",
            "icon": "bi-people-fill",
            "url": "public_board",  # 👈 Goes to new grid dashboard
        },
    ]
    return render(request, "core/landing.html", {"brands": brands})
