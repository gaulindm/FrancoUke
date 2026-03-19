"""
francontcube/views/puzzles/puzzle_2x2.py
Vues pour le 2x2 — flexible pour accueillir Ortega, CLL, EG plus tard.
"""

from django.shortcuts import render, get_object_or_404
from cube.models import PuzzleCase


# Catalogue des méthodes 2x2 disponibles
METHODS_2X2 = {
    'ortega': {
        'name':        'Méthode Ortega',
        'desc':        'La méthode la plus accessible pour le 2×2. 3 étapes simples.',
        'steps': [
            {
                'slug':  'face',
                'name':  'Étape 1 — Face',
                'desc':  'Résoudre une face (pas besoin que les côtés matchent).',
                'icon':  'bi-square',
            },
            {
                'slug':  'oll',
                'name':  'Étape 2 — OLL',
                'desc':  'Orienter la dernière couche (7 cas).',
                'icon':  'bi-arrow-repeat',
            },
            {
                'slug':  'pbl',
                'name':  'Étape 3 — PBL',
                'desc':  'Permuter les deux couches (6 cas).',
                'icon':  'bi-shuffle',
            },
        ],
    },
    # Ajouter CLL, EG1, EG2 ici plus tard
}


def puzzle_2x2_home(request):
    """Page d'accueil du 2x2 — liste les méthodes disponibles."""
    return render(request, 'francontcube/puzzles/2x2/home.html', {
        'methods': METHODS_2X2,
        'puzzle_type': '2x2',
    })


def puzzle_2x2_method(request, method):
    """
    Vue d'ensemble d'une méthode 2x2.
    Ex: /puzzles/2x2/ortega/  → montre les 3 étapes Ortega
    """
    method_data = METHODS_2X2.get(method)
    if not method_data:
        from django.http import Http404
        raise Http404(f"Méthode 2x2 inconnue : {method}")

    return render(request, 'francontcube/puzzles/2x2/method.html', {
        'method_slug': method,
        'method':      method_data,
        'puzzle_type': '2x2',
    })


def puzzle_2x2_step(request, method, step):
    """
    Page d'une étape spécifique du 2x2.
    Ex: /puzzles/2x2/ortega/pbl/  → tous les cas PBL
    """
    method_data = METHODS_2X2.get(method)
    if not method_data:
        from django.http import Http404
        raise Http404(f"Méthode 2x2 inconnue : {method}")

    # Trouver les infos de l'étape dans le catalogue
    step_info = next(
        (s for s in method_data['steps'] if s['slug'] == step),
        None
    )
    if not step_info:
        from django.http import Http404
        raise Http404(f"Étape inconnue : {step}")

    # Récupérer les cas depuis la BD
    cases = PuzzleCase.objects.filter(
        puzzle_type='2x2',
        method=method,
        category=step,
    ).order_by('step_number')

    return render(request, 'francontcube/puzzles/2x2/step.html', {
        'method_slug': method,
        'method':      method_data,
        'step':        step_info,
        'cases':       cases,
        'puzzle_type': '2x2',
    })