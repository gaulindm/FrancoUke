"""
Apprenti Cubi method overview page.

Displays the list of all steps in the method with their descriptions.
"""

from django.shortcuts import render
from cube.models import CubeState
import json


def method_cubienewbie(request):
    """
    Main overview page for Apprenti Cubi method.
    
    Shows all 11 items (3 intro + 7 solving steps + 1 final) with descriptions,
    icons, cube states, and availability status.
    """
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '', 'icon': 'star-fill'},
    ]
    
    # Helper function to get cube state safely
    def get_cube_state(slug):
        try:
            state = CubeState.objects.get(slug=slug)
            # json_state is already a dict (JSONField), just return it as JSON string
            return json.dumps(state.json_state)
        except CubeState.DoesNotExist:
            return None
    
    steps = [
        {
            "name": "1 — A propos",
            "desc": "Au sujet de la méthode présenté pour les nouveaux cubeurs",
            "icon": "bi-cube",
            "url": "/francontcube/methods/cubienewbie/about/",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "2 — Le cube",
            "desc": "Comprendre les pièces, la structure et le fonctionnement.",
            "icon": "bi-cube",
            "url": "/francontcube/methods/cubienewbie/cube/",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "3 — La notation",
            "desc": "Apprendre comment lire les mouvements (R, L, U, F…).",
            "icon": "bi-pencil",
            "url": "/francontcube/methods/cubienewbie/notation/",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "4 — Étape 1: La marguerite",
            "desc": "Premier objectif : construire la marguerite autour du centre jaune.",
            "icon": "bi-flower3",
            "url": "/francontcube/methods/cubienewbie/daisy/",
            "available": True,
            "cube_state": get_cube_state('marguerite-goal')
        },
        {
            "name": "5 — Étape 2 : La croix blanche",
            "desc": "Aligner les arêtes blanches avec les centres pour former la croix.",
            "icon": "bi-plus-circle",
            "url": "/francontcube/methods/cubienewbie/white-cross/",
            "available": True,
            "cube_state": get_cube_state('white-cross-goal')
        },
        {
            "name": "6 — Étape 3 : Les coins inférieurs",
            "desc": "Placer les coins inferieurs blancs pour compléter la première couche.",
            "icon": "bi-box",
            "url": "/francontcube/methods/cubienewbie/bottom-corners/",
            "available": True,
            "cube_state": get_cube_state('bottom-corners-goal')
        },
        {
            "name": "7 — Étape 4 : Les bords du milieu",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": "/francontcube/methods/cubienewbie/second-layer/",
            "available": True,
            "cube_state": get_cube_state('second-layer-goal')
        },
        {
            "name": "8 — Étape 5 : La croix jaune",
            "desc": "Former la croix jaune sur la face supérieure.",
            "icon": "bi-plus-circle",
            "url": "/francontcube/methods/cubienewbie/yellow-cross/",
            "available": True,
            "cube_state": get_cube_state('yellow-cross-goal')
        },
        {
            "name": "9 — Étape 6 : La face jaune",
            "desc": "La chasse au poisson.",
            "icon": "bi-brightness-high",
            "url": "/francontcube/methods/cubienewbie/yellow-face/",
            "available": True,
            "cube_state": get_cube_state('yellow-face-goal')
        },
        {
            "name": "10 — Étape 7 : La permutation des coins jaunes",
            "desc": "Placer les coins à leur bon emplacement.",
            "icon": "bi-arrow-repeat",
            "url": "/francontcube/methods/cubienewbie/corner-permutation/",
            "available": True,
            "cube_state": get_cube_state('corner-perm-goal')
        },
        {
            "name": "11 — Étape 8 : La permutation des arêtes",    
            "desc": "La permutation des arêtes de la couche jaune pour finir le cube.",
            "icon": "bi-check-circle",
            "url": "/francontcube/methods/cubienewbie/edge-permutation/",
            "available": True,
            "cube_state": get_cube_state('edge-perm-goal-needsu')  # Final solved cube
        },
    ]

    return render(request, "francontcube/methods/cubienewbie/index.html", {
        "steps": steps,
        "breadcrumbs": breadcrumbs
    })