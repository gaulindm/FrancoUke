"""
PLL Introduction page - Detailed explanation of the PLL step.

This page explains:
- What is PLL (Permutation of Last Layer)
- The 21 PLL algorithms organized by patterns
- 2-Look PLL for beginners
- Recognition tips and practice strategies
"""

from django.shortcuts import render
from django.urls import reverse


def cfop_pll_intro(request):
    """
    Introduction page for PLL (Permutation of Last Layer).
    
    Provides detailed explanation before users access the algorithms.
    """
    breadcrumbs = [
        {'name': 'Accueil', 'url': reverse('francontcube:home')},
        {'name': 'CFOP', 'url': reverse('francontcube:method_cfop')},
        {'name': 'PLL - Introduction', 'url': ''},
    ]
    
    # PLL Pattern Groups
    pll_groups = [
        {
            'name': 'Permutations d\'Arêtes (4 cas)',
            'icon': 'bi-arrows-move',
            'color': 'primary',
            'description': 'Seules les arêtes doivent être permutées. Les coins sont déjà en place.',
            'difficulty': 'Facile',
            'cases': ['Ua', 'Ub', 'Z', 'H'],
            'tip': 'Les plus faciles à reconnaître - regardez les barres de couleur.',
        },
        {
            'name': 'Permutations de Coins (4 cas)',
            'icon': 'bi-box',
            'color': 'success',
            'description': 'Seuls les coins doivent être permutés. Les arêtes sont déjà en place.',
            'difficulty': 'Facile',
            'cases': ['Aa', 'Ab', 'E'],
            'tip': 'Cherchez les coins qui doivent être échangés (headlights pattern).',
        },
        {
            'name': 'Permutations Adjacentes (8 cas)',
            'icon': 'bi-arrow-left-right',
            'color': 'warning',
            'description': 'Tous les coins et arêtes d\'un côté doivent être échangés.',
            'difficulty': 'Moyen',
            'cases': ['T', 'Ja', 'Jb', 'F', 'Ra', 'Rb', 'Ga', 'Gb', 'Gc', 'Gd'],
            'tip': 'Pattern "2 coins + 2 arêtes" du même côté.',
        },
        {
            'name': 'Permutations Diagonales (5 cas)',
            'icon': 'bi-arrow-down-up',
            'color': 'danger',
            'description': 'Les coins en diagonale doivent être échangés.',
            'difficulty': 'Difficile',
            'cases': ['V', 'Y', 'Na', 'Nb'],
            'tip': 'Les plus difficiles à reconnaître - regardez les diagonales.',
        },
    ]
    
    # 2-Look PLL Strategy
    two_look_pll = {
        'step1': {
            'title': 'Étape 1 : Permuter les Coins',
            'desc': 'Utilisez un seul algorithme pour placer tous les coins correctement',
            'algorithm': {
                'name': 'A Perm (Aa ou Ab)',
                'alg': 'x (R\' U R\') D2 (R U\' R\') D2 R2 x\'',
                'alt_alg': 'ou x R2 D2 (R U R\') D2 (R U\' R) x\'',
                'pattern': 'Échangez 3 coins dans le sens horaire ou anti-horaire',
            },
            'cases_count': 2,
            'note': 'Positionnez le coin déjà correct à l\'arrière-droite avant d\'exécuter.',
        },
        'step2': {
            'title': 'Étape 2 : Permuter les Arêtes',
            'desc': 'Utilisez un seul algorithme pour placer toutes les arêtes',
            'algorithm': {
                'name': 'U Perm (Ua ou Ub)',
                'alg_ua': 'M2 U M U2 M\' U M2',
                'alg_ub': 'M2 U\' M U2 M\' U\' M2',
                'pattern': 'Échangez 3 arêtes (clockwise = Ua, counter = Ub)',
            },
            'cases_count': 4,
            'note': 'Positionnez l\'arête déjà correcte à l\'arrière avant d\'exécuter.',
        },
    }
    
    # Recognition guide
    recognition_tips = [
        {
            'title': 'Headlights',
            'desc': 'Deux stickers de même couleur adjacents sur une face = coins déjà placés',
            'icon': 'bi-lightbulb',
        },
        {
            'title': 'Bars',
            'desc': 'Une ligne de couleur unie = arêtes déjà alignées sur cette face',
            'icon': 'bi-distribute-horizontal',
        },
        {
            'title': 'Blocks',
            'desc': 'Un bloc 2x1 de même couleur = coin + arête adjacents déjà placés',
            'icon': 'bi-grid-1x2',
        },
        {
            'title': '2-2 Split',
            'desc': 'Deux paires de couleurs opposées = souvent un N perm ou H perm',
            'icon': 'bi-symmetry-vertical',
        },
    ]
    
    # Learning tips
    tips = [
        {
            'icon': 'bi-trophy',
            'title': 'Apprenez les U Perms en Premier',
            'desc': 'Ua et Ub sont les PLL les plus fréquents (~20% des solves). Maîtrisez-les parfaitement.',
        },
        {
            'icon': 'bi-eye-fill',
            'title': 'Reconnaissance AUF',
            'desc': 'Avant d\'exécuter le PLL, faites un AUF pour mettre le pattern dans la bonne orientation.',
        },
        {
            'icon': 'bi-arrow-clockwise',
            'title': 'M Moves = Rapidité',
            'desc': 'Les algorithmes avec M moves (M, M2) sont plus rapides. Entraînez-vous à les exécuter fluidement.',
        },
        {
            'icon': 'bi-palette',
            'title': 'Color Neutrality',
            'desc': 'Apprenez à reconnaître les patterns indépendamment de la couleur de la face supérieure.',
        },
        {
            'icon': 'bi-graph-up',
            'title': 'Progression Logique',
            'desc': 'Ordre recommandé: U perms → A perms → T & J perms → G perms → diagonaux (N, V, Y)',
        },
        {
            'icon': 'bi-speedometer',
            'title': 'TPS (Turns Per Second)',
            'desc': 'Un bon PLL = 4-6 TPS. Chronométrez vos algorithmes pour suivre vos progrès.',
        },
    ]
    
    # Most common PLLs
    common_plls = [
        {'name': 'Ua', 'frequency': '~18%', 'color': 'primary'},
        {'name': 'Ub', 'frequency': '~18%', 'color': 'primary'},
        {'name': 'T', 'frequency': '~7%', 'color': 'success'},
        {'name': 'Aa', 'frequency': '~7%', 'color': 'success'},
        {'name': 'Ab', 'frequency': '~7%', 'color': 'success'},
        {'name': 'H', 'frequency': '~5%', 'color': 'warning'},
        {'name': 'Z', 'frequency': '~5%', 'color': 'warning'},
        {'name': 'Autres (14)', 'frequency': '~33%', 'color': 'secondary'},
    ]
    
    context = {
        'breadcrumbs': breadcrumbs,
        'pll_groups': pll_groups,
        'two_look_pll': two_look_pll,
        'recognition_tips': recognition_tips,
        'tips': tips,
        'common_plls': common_plls,
        'total_pll_cases': 21,
        'two_look_count': 6,
    }
    
    return render(request, 'francontcube/methods/cfop/pll_intro.html', context)