from django.shortcuts import render


def landing_page(request):
    ukulele_brands = [
        {"name": "FrancoUke", "desc": "Votre outil idéal pour générer des PDF de qualité de chansons pour tous les instruments à cordes pincées.", 
         "icon": "bi-music-note-beamed", "url": "francouke:home"},
        {"name": "StrumSphere", "desc": "Your perfect tool to render quality PDF of songs for all strumming instruments.", 
         "icon": "bi-vinyl", "url": "strumsphere:home"},
        {"name": "Uke4ia", "desc": "Your gateway to ukulele euphoria.", 
         "icon": "bi-star-fill", "url": "uke4ia:home"},
    ]
    return render(request, "core/landing.html", {"brands": ukulele_brands})