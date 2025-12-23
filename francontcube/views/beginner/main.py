"""
Beginner method overview page.
"""

from django.shortcuts import render
from django.urls import reverse


def method_beginner(request):
    """
    Main overview page for the Beginner method.
    """
    breadcrumbs = [
        {'name': 'Méthodes', 'url': reverse('francontcube:home'), 'icon': 'book'},
        {'name': 'Débutant', 'url': '', 'icon': 'star-fill'},  # Page actuelle, URL vide
    ]
    
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
            "url": reverse('francontcube:beginner_white_cross'),
            "available": True,
            "step_number": 1,
        },
        {
            "name": "Étape 2 : Les coins inférieurs",
            "desc": "Placer les coins inférieurs blancs pour compléter la première couche.",
            "icon": "bi-box",
            "url": reverse('francontcube:beginner_bottom_corners'),
            "available": True,
            "step_number": 2,
        },
        {
            "name": "Étape 3 : Les bords du milieu",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": reverse('francontcube:beginner_second_layer'),
            "available": True,
            "step_number": 3,
        },
        {
            "name": "Étape 4 : La croix jaune",
            "desc": "Former la croix jaune sur la face supérieure.",
            "icon": "bi-plus-circle",
            "url": reverse('francontcube:beginner_yellow_cross'),
            "available": True,
            "step_number": 4,
        },
        {
            "name": "Étape 5 : La face jaune",
            "desc": "Orienter tous les coins pour compléter la face jaune (la chasse au poisson).",
            "icon": "bi-brightness-high",
            "url": reverse('francontcube:beginner_yellow_face'),
            "available": True,
            "step_number": 5,
        },
        {
            "name": "Étape 6 : La permutation des coins",
            "desc": "Placer les coins jaunes à leur bon emplacement.",
            "icon": "bi-arrow-repeat",
            "url": reverse('francontcube:beginner_corner_permutation'),
            "available": True,
            "step_number": 6,
        },
        {
            "name": "Étape 7 : La permutation des arêtes",    
            "desc": "Permuter les arêtes de la couche jaune pour finir le cube.",
            "icon": "bi-check-circle",
            "url": reverse('francontcube:beginner_edge_permutation'),
            "available": True,
            "step_number": 7,
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