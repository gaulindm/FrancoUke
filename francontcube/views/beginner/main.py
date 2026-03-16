"""
Beginner method overview page.
"""

from django.shortcuts import render
from django.urls import reverse
from cube.models import CubeState
import json



def method_beginner(request):
    """
    Main overview page for the Beginner method.
    """
    breadcrumbs = [
        {'name': 'Méthodes', 'url': reverse('francontcube:home'), 'icon': 'book'},
        {'name': 'Débutant', 'url': '', 'icon': 'star-fill'},  # Page actuelle, URL vide
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
            "name": "À propos",
            "desc": "Présentation de la méthode débutant pour résoudre le Rubik's Cube",
            "icon": "bi-info-circle",
            "url": reverse('francontcube:beginner_about'),
            "available": True,
            "step_number": None,
        },
        {
            "name": "Étape 1 : La croix blanche",
            "desc": "Aligner les arêtes blanches avec les centres pour former la croix.",
            "icon": "bi-plus-circle",
            "url": reverse('francontcube:beginner_bottom_cross'),
            "available": True,
            "step_number": 1,
            "cube_state": get_cube_state('bottom-cross-goal')

        },
        {
            "name": "Étape 2 : Les coins inférieurs",
            "desc": "Placer les coins inférieurs jaunes pour compléter la première couche.",
            "icon": "bi-box",
            "url": reverse('francontcube:beginner_bottom_corners'),
            "available": True,
            "step_number": 2,
            "cube_state": get_cube_state('bottom-corners-goal')

        },
        {
            "name": "Étape 3 : Les bords du milieu",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": reverse('francontcube:beginner_second_layer'),
            "available": True,
            "step_number": 3,
            "cube_state": get_cube_state('second-layer-goal')

        },
        {
            "name": "Étape 4 : La croix superieur",
            "desc": "Former la croix blanche sur la face supérieure.",
            "icon": "bi-plus-circle",
            "url": reverse('francontcube:beginner_top_cross'),
            "available": True,
            "step_number": 4,
            "cube_state": get_cube_state('top-cross-goal')

        },
        {
            "name": "Étape 5 : La face jaune",
            "desc": "Orienter tous les coins pour compléter la face blanche (la chasse au poisson).",
            "icon": "bi-brightness-high",
            "url": reverse('francontcube:beginner_top_face'),
            "available": True,
            "step_number": 5,
            "cube_state": get_cube_state('top-face-goal')

        },
        {
            "name": "Étape 6 : La permutation des coins",
            "desc": "Placer les coins blancs à leur bon emplacement.",
            "icon": "bi-arrow-repeat",
            "url": reverse('francontcube:beginner_corner_permutation'),
            "available": True,
            "step_number": 6,
            "cube_state": get_cube_state('corner-perm-goal')

        },
        {
            "name": "Étape 7 : La permutation des arêtes",    
            "desc": "Permuter les arêtes de la couche du haut pour finir le cube.",
            "icon": "bi-check-circle",
            "url": reverse('francontcube:beginner_edge_permutation'),
            "available": True,
            "step_number": 7,
            "cube_state": get_cube_state('edge-perm-goal-needsu')  # Final solved cube

        },
    ]
    
    context = {
        "steps": steps,
        "breadcrumbs": breadcrumbs,
        "method_name": "Méthode Débutant",
        "method_description": "Une méthode efficace en 7 étapes pour résoudre le Rubik's Cube 3x3",
        "total_steps": 7,
        "difficulty": "Débutant",
        "estimated_time": "3-4 heures d'apprentissage",
    }

    return render(request, "francontcube/methods/beginner/index.html", context)