"""
francontcube/views/puzzles/puzzle_4x4.py
francontcube/views/puzzles/puzzle_5x5.py

Les deux utilisent la méthode Reduction — structure identique.
Un seul fichier pour éviter la duplication, paramétré par puzzle_type.
"""

from django.shortcuts import render
from django.http import Http404
from cube.models import PuzzleCase


# ── Catalogues des étapes ──────────────────────────────────────────────────

STEPS_4X4 = [
    {
        'slug':  'centers',
        'name':  'Étape 1 — Centres',
        'desc':  'Assembler les 6 centres (3×3 de stickers par face).',
        'icon':  'bi-circle',
        'tip':   'Commence par les centres opposés : blanc/jaune, puis les 4 latéraux.',
    },
    {
        'slug':  'edges',
        'name':  'Étape 2 — Arêtes',
        'desc':  'Regrouper les 12 paires d\'arêtes (edge pairing).',
        'icon':  'bi-arrows-collapse',
        'tip':   'Garde toujours une arête libre pour le wing flip.',
    },
    {
        'slug':  'parity',
        'name':  'Étape 3 — Parité',
        'desc':  'Corriger les cas de parité OLL et PLL spécifiques au 4×4.',
        'icon':  'bi-exclamation-triangle',
        'tip':   'La parité arrive ~50% du temps. Apprends les 2 algorithmes.',
    },
    {
        'slug':  '3x3-phase',
        'name':  'Étape 4 — Phase 3×3',
        'desc':  'Résoudre comme un 3×3 (CFOP ou méthode débutant).',
        'icon':  'bi-grid-3x3',
        'tip':   'Tu connais déjà cette partie — utilise ta méthode habituelle!',
    },
]

STEPS_5X5 = [
    {
        'slug':  'centers',
        'name':  'Étape 1 — Centres',
        'desc':  'Assembler les 6 centres (3×3 de stickers chacun).',
        'icon':  'bi-circle',
        'tip':   'Commence par blanc/jaune pour avoir un point de référence.',
    },
    {
        'slug':  'edges',
        'name':  'Étape 2 — Arêtes',
        'desc':  'Regrouper les 12 trios d\'arêtes.',
        'icon':  'bi-arrows-collapse',
        'tip':   'Les 8 premières arêtes librement, les 4 dernières avec soin.',
    },
    {
        'slug':  'last-centers',
        'name':  'Étape 3 — Derniers centres',
        'desc':  'Corriger les centres perturbés pendant l\'étape arêtes.',
        'icon':  'bi-arrow-clockwise',
        'tip':   'Souvent inutile si tu es prudent à l\'étape 2.',
    },
    {
        'slug':  'last-edges',
        'name':  'Étape 4 — Dernières arêtes',
        'desc':  'Finir les arêtes restantes sans casser les centres.',
        'icon':  'bi-arrows-expand',
        'tip':   '',
    },
    {
        'slug':  'parity',
        'name':  'Étape 5 — Parité',
        'desc':  'Gérer les cas de parité propres au 5×5.',
        'icon':  'bi-exclamation-triangle',
        'tip':   'La parité du 5×5 est similaire au 4×4 — mêmes algos souvent.',
    },
    {
        'slug':  '3x3-phase',
        'name':  'Étape 6 — Phase 3×3',
        'desc':  'Résoudre comme un 3×3.',
        'icon':  'bi-grid-3x3',
        'tip':   '',
    },
]

PUZZLE_CONFIGS = {
    '4x4': {
        'name':   '4×4 — Revenge',
        'method': 'reduction',
        'steps':  STEPS_4X4,
    },
    '5x5': {
        'name':   '5×5 — Professor',
        'method': 'reduction',
        'steps':  STEPS_5X5,
    },
}


# ── Vues réutilisables ─────────────────────────────────────────────────────

def _get_config(puzzle_type):
    config = PUZZLE_CONFIGS.get(puzzle_type)
    if not config:
        raise Http404(f"Puzzle inconnu : {puzzle_type}")
    return config


def puzzle_big_home(request, puzzle_type):
    """
    Page d'accueil d'un grand cube (4x4 ou 5x5).
    Affiche toutes les étapes de la méthode Reduction.
    """
    config = _get_config(puzzle_type)
    return render(request, 'francontcube/puzzles/big_cube/home.html', {
        'config':      config,
        'puzzle_type': puzzle_type,
    })


def puzzle_big_step(request, puzzle_type, step):
    """
    Page d'une étape spécifique (4x4 ou 5x5).
    Ex: /puzzles/4x4/parity/
    """
    config = _get_config(puzzle_type)

    step_info = next(
        (s for s in config['steps'] if s['slug'] == step),
        None
    )
    if not step_info:
        raise Http404(f"Étape inconnue : {step}")

    cases = PuzzleCase.objects.filter(
        puzzle_type=puzzle_type,
        method=config['method'],
        category=step,
    ).order_by('step_number')

    # Étapes précédente et suivante pour la navigation
    all_slugs = [s['slug'] for s in config['steps']]
    current_index = all_slugs.index(step)
    prev_step = config['steps'][current_index - 1] if current_index > 0 else None
    next_step = config['steps'][current_index + 1] if current_index < len(all_slugs) - 1 else None

    return render(request, 'francontcube/puzzles/big_cube/step.html', {
        'config':      config,
        'step':        step_info,
        'cases':       cases,
        'puzzle_type': puzzle_type,
        'prev_step':   prev_step,
        'next_step':   next_step,
    })


# ── Raccourcis pour les URLs nommées ──────────────────────────────────────

def puzzle_4x4_home(request):
    return puzzle_big_home(request, '4x4')

def puzzle_4x4_step(request, step):
    return puzzle_big_step(request, '4x4', step)

def puzzle_5x5_home(request):
    return puzzle_big_home(request, '5x5')

def puzzle_5x5_step(request, step):
    return puzzle_big_step(request, '5x5', step)