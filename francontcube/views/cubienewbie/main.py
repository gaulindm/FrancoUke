"""
Apprenti Cubi method overview page.

Displays the list of all steps in the method with their descriptions.
"""

from django.shortcuts import render


def method_cubienewbie(request):
    """
    Main overview page for Apprenti Cubi method.
    
    Shows all 10 items (2 intro + 7 solving steps + 1 final) with descriptions,
    icons, and availability status.
    """
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '', 'icon': 'star-fill'},
    ]
    
    steps = [
        {
            "name": "1 — A propos",
            "desc": "Au sujet de la méthode présenté pour les nouveaux cubeurs",
            "icon": "bi-cube",
            "url": "/francontcube/methods/cubienewbie/about/",
            "available": True
        },
        {
            "name": "2 — Le cube",
            "desc": "Comprendre les pièces, la structure et le fonctionnement.",
            "icon": "bi-cube",
            "url": "/francontcube/methods/cubienewbie/cube/",
            "available": True
        },
        {
            "name": "3 — La notation",
            "desc": "Apprendre comment lire les mouvements (R, L, U, F…).",
            "icon": "bi-pencil",
            "url": "/francontcube/methods/cubienewbie/notation/",
            "available": True,
        },
        {
            "name": "4 — Étape 1a : La marguerite",
            "desc": "Premier objectif : construire la marguerite autour du centre jaune.",
            "icon": "bi-flower3",
            "url": "/francontcube/methods/cubienewbie/daisy/",
            "available": True,
        },
        {
            "name": "5 — Étape 1b : La croix blanche",
            "desc": "Aligner les arêtes blanches avec les centres pour former la croix.",
            "icon": "bi-plus-circle",
            "url": "/francontcube/methods/cubienewbie/white-cross/",
            "available": True,
        },
        {
            "name": "6 — Étape 2 : Les coins inférieurs",
            "desc": "Placer les coins inferieurs blancs pour compléter la première couche.",
            "icon": "bi-box",
            "url": "/francontcube/methods/cubienewbie/bottom-corners/",
            "available": True,
        },
        {
            "name": "7 — Étape 3 : Les bords du milieu",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": "/francontcube/methods/cubienewbie/second-layer/",
            "available": True,
        },
        {
            "name": "8 — Étape 4 : La croix jaune",
            "desc": "Former la croix jaune sur la face supérieure.",
            "icon": "bi-plus-circle",
            "url": "/francontcube/methods/cubienewbie/yellow-cross/",
            "available": True,
        },
        {
            "name": "9 — Étape 5 : La face jaune",
            "desc": "La chasse au poisson.",
            "icon": "bi-brightness-high",
            "url": "/francontcube/methods/cubienewbie/yellow-face/",
            "available": True,
        },
        {
            "name": "10 — Étape 6 : La permutation des coins jaunes",
            "desc": "Placer les coins à leur bon emplacement.",
            "icon": "bi-arrow-repeat",
            "url": "/francontcube/methods/cubienewbie/corner-permutation/",
            "available": True,
        },
        {
            "name": "11 — Étape 7 : La permutation des arêtes",    
            "desc": "La permutation des arêtes de la couche jaune pour finir le cube.",
            "icon": "bi-check-circle",
            "url": "/francontcube/methods/cubienewbie/edge-permutation/",
            "available": True,
        },
    ]

    return render(request, "francontcube/methods/cubienewbie/index.html", {
        "steps": steps,
        "breadcrumbs": breadcrumbs
    })