"""
francontcube/views/puzzles/home.py
Page d'accueil pour les autres casse-têtes (2x2, 4x4, 5x5).
"""

from django.shortcuts import render


# Catalogue des puzzles disponibles
# Facile à étendre : ajouter un dict pour un nouveau puzzle
PUZZLES = [
    {
        'puzzle_type': '2x2',
        'name':        '2×2 — Pocket Cube',
        'desc':        'Le petit frère du 3×3. Apprends la méthode Ortega.',
        'icon':        'bi-grid',
        'url':         '/francontcube/puzzles/2x2/',
        'available':   True,
    },
    {
        'puzzle_type': '4x4',
        'name':        '4×4 — Revenge',
        'desc':        'Méthode Reduction : centres, arêtes, puis phase 3×3.',
        'icon':        'bi-grid-fill',
        'url':         '/francontcube/puzzles/4x4/',
        'available':   True,
    },
    {
        'puzzle_type': '5x5',
        'name':        '5×5 — Professor',
        'desc':        'Méthode Reduction étendue avec gestion de la parité.',
        'icon':        'bi-grid-3x3-gap-fill',
        'url':         '/francontcube/puzzles/5x5/',
        'available':   True,
    },
]


def puzzles_home(request):
    """Page d'accueil listant tous les puzzles disponibles."""
    return render(request, 'francontcube/puzzles/home.html', {
        'puzzles': PUZZLES,
    })