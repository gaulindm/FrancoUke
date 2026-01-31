"""
CFOP method overview page.

CFOP is an advanced speedcubing method consisting of 4 steps:
- Cross: White cross on bottom
- F2L: First Two Layers (4 pairs)
- OLL: Orientation of Last Layer (57 algorithms)
- PLL: Permutation of Last Layer (21 algorithms)
"""

from django.shortcuts import render
from django.urls import reverse


def method_cfop(request):
    """
    Main overview page for the CFOP method.
    
    Shows all steps with descriptions, icons, and availability status.
    """
    breadcrumbs = [
        {'name': 'Accueil', 'url': reverse('francontcube:home')},
        {'name': 'CFOP', 'url': ''},
    ]
    
    steps = [
        {
            "name": "À propos",
            "desc": "Introduction à la méthode CFOP pour le speedcubing avancé",
            "icon": "bi-info-circle",
            "url": reverse('francontcube:cfop_about'),
            "available": True,
            "step_number": None,
        },
        {
            "name": "🌉 De Débutant à F2L",  # ⬅️ NOUVEAU
            "desc": "Découvrez comment l'algo de 2e couche est en fait du F2L!",
            "icon": "bi-lightbulb-fill",
            "url": reverse('francontcube:beginner_to_f2l'),
            "available": True,
            "step_number": None,
            "highlight": True,  # Pour le mettre en évidence
        },
        {
            "name": "Étape 1 : Cross",
            "desc": "Résoudre la croix blanche en bas (idéalement en moins de 8 mouvements).",
            "icon": "bi-plus-circle",
            "url": reverse('francontcube:cfop_cross'),
            "available": True,
            "step_number": 1,
        },
        {
            "name": "Étape 2 : F2L",
            "desc": "Résoudre les deux premières couches simultanément (4 paires coin-arête).",
            "icon": "bi-layers",
            "url": reverse('francontcube:cfop_f2l_intro'),  # <-- Changement ici
            "available": True,
            "step_number": 2,
            "sub_pages": [  # Optionnel: ajouter des sous-pages
                {
                    "name": "Introduction F2L",
                    "url": reverse('francontcube:cfop_f2l_intro'),
                },
                {
                    "name": "Les 41 Cas",
                    "url": reverse('francontcube:cfop_f2l_basic'),
                },
            ],
        },
        {
            "name": "Étape 3 : OLL",
            "desc": "Orienter la dernière couche pour avoir la face jaune complète (57 cas).",
            "icon": "bi-brightness-high",
            "url": reverse('francontcube:cfop_oll'),
            "available": False,
            "step_number": 3,
        },
        {
            "name": "Étape 4 : PLL",
            "desc": "Permuter la dernière couche pour finir le cube (21 cas).",
            "icon": "bi-shuffle",
            "url": reverse('francontcube:cfop_pll'),
            "available": False,
            "step_number": 4,
        },
    ]
    
    context = {
        "steps": steps,
        "breadcrumbs": breadcrumbs,
        "method_name": "CFOP",
        "method_description": "La méthode de speedcubing la plus populaire au monde",
        "total_steps": 4,
        "difficulty": "Avancé",
        "estimated_time": "Plusieurs semaines d'apprentissage",
        "algorithms_count": "78+ algorithmes (57 OLL + 21 PLL)",
    }

    return render(request, "francontcube/methods/cfop/index.html", context)