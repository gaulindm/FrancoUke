"""
OLL Introduction page - Detailed explanation of the OLL step.

This page explains:
- What is OLL (Orientation of Last Layer)
- The 57 OLL algorithms organized by patterns
- 2-Look OLL for beginners
- Recognition tips and practice strategies
"""

from django.shortcuts import render
from django.urls import reverse


def cfop_oll_intro(request):
    """
    Introduction page for OLL (Orientation of Last Layer).
    
    Provides detailed explanation before users access the algorithms.
    """
    breadcrumbs = [
        {'name': 'Accueil', 'url': reverse('francontcube:home')},
        {'name': 'CFOP', 'url': reverse('francontcube:method_cfop')},
        {'name': 'OLL - Introduction', 'url': ''},
    ]
    
    # OLL Pattern Groups
    oll_groups = [
        {
            'name': 'Croix (8 cas)',
            'icon': 'bi-plus-circle',
            'color': 'primary',
            'description': 'Une croix jaune est déjà formée sur le dessus. Il faut orienter les coins.',
            'difficulty': 'Facile',
            'cases': 'OLL #20-27',
        },
        {
            'name': 'Point (4 cas)',
            'icon': 'bi-dot',
            'color': 'danger',
            'description': 'Aucune arête jaune orientée. Le cas le moins favorable.',
            'difficulty': 'Moyen',
            'cases': 'OLL #1-4',
        },
        {
            'name': 'Ligne (6 cas)',
            'icon': 'bi-dash-lg',
            'color': 'warning',
            'description': 'Deux arêtes jaunes opposées forment une ligne.',
            'difficulty': 'Facile',
            'cases': 'OLL #51-56',
        },
        {
            'name': 'L Shape (6 cas)',
            'icon': 'bi-caret-right-fill',
            'color': 'info',
            'description': 'Deux arêtes jaunes adjacentes forment un L.',
            'difficulty': 'Moyen',
            'cases': 'OLL #45-50',
        },
        {
            'name': 'T Shape (3 cas)',
            'icon': 'bi-justify',
            'color': 'success',
            'description': 'Trois arêtes orientées formant un T.',
            'difficulty': 'Facile',
            'cases': 'OLL #33, 37, 45',
        },
        {
            'name': 'C Shape (2 cas)',
            'icon': 'bi-reception-4',
            'color': 'secondary',
            'description': 'Deux arêtes opposées non orientées.',
            'difficulty': 'Moyen',
            'cases': 'OLL #34, 46',
        },
        {
            'name': 'P Shape (4 cas)',
            'icon': 'bi-flag',
            'color': 'primary',
            'description': 'Configuration en forme de P.',
            'difficulty': 'Moyen',
            'cases': 'OLL #31-32, 43-44',
        },
        {
            'name': 'W, Z, Autres (24 cas)',
            'icon': 'bi-grid-3x3',
            'color': 'dark',
            'description': 'Patterns moins fréquents mais importants.',
            'difficulty': 'Varié',
            'cases': 'OLL divers',
        },
    ]
    
    # 2-Look OLL Strategy
    two_look_oll = {
        'step1': {
            'title': 'Étape 1 : Former la Croix Jaune',
            'desc': 'Utilisez seulement 3 algorithmes pour former la croix',
            'algorithms': [
                {'name': 'Point → Ligne', 'alg': 'F (R U R\' U\') F\'', 'pattern': 'Aucune arête'},
                {'name': 'L Shape → Ligne', 'alg': 'f (R U R\' U\') f\'', 'pattern': '2 arêtes adjacentes'},
                {'name': 'Ligne → Croix', 'alg': 'F (R U R\' U\') F\'', 'pattern': '2 arêtes opposées'},
            ],
            'cases_count': 3,
        },
        'step2': {
            'title': 'Étape 2 : Orienter les Coins',
            'desc': 'Utilisez 4 algorithmes pour orienter les coins jaunes',
            'algorithms': [
                {'name': 'Sune', 'alg': 'R U R\' U R U2 R\'', 'pattern': '1 coin bien orienté à gauche-devant'},
                {'name': 'Anti-Sune', 'alg': 'R U2 R\' U\' R U\' R\'', 'pattern': '1 coin bien orienté à droite-devant'},
                {'name': 'H', 'alg': 'R U R\' U R U\' R\' U R U2 R\'', 'pattern': 'Coins opposés mal orientés'},
                {'name': 'Pi', 'alg': 'R U2 R2 U\' R2 U\' R2 U2 R', 'pattern': 'Tous les coins mal orientés'},
            ],
            'cases_count': 7,
        },
    }
    
    # Learning tips
    tips = [
        {
            'icon': 'bi-eye',
            'title': 'Reconnaissance des Patterns',
            'desc': 'Identifiez d\'abord le pattern de la croix (point, ligne, L, croix). Ensuite regardez les coins.',
        },
        {
            'icon': 'bi-speedometer2',
            'title': 'Commencez avec 2-Look OLL',
            'desc': 'Maîtrisez d\'abord les 10 algorithmes de base du 2-Look OLL avant d\'apprendre les 57 cas.',
        },
        {
            'icon': 'bi-arrow-repeat',
            'title': 'Rotation AUF',
            'desc': 'Apprenez à faire des AUF (Adjust Upper Face) rapides pour aligner les patterns correctement.',
        },
        {
            'icon': 'bi-lightning-charge',
            'title': 'Algorithmes Mirrors',
            'desc': 'Plusieurs OLL ont des versions miroirs. Apprenez-les par paires pour doubler votre efficacité.',
        },
        {
            'icon': 'bi-bookmark-check',
            'title': 'Cas Fréquents d\'Abord',
            'desc': 'Certains OLL apparaissent plus souvent. Priorisez OLL #21, #22, #23, #24 (les T et L shapes).',
        },
        {
            'icon': 'bi-cpu',
            'title': 'Muscle Memory',
            'desc': 'Répétez chaque algorithme 50+ fois lentement avant de chercher la vitesse.',
        },
    ]
    
    context = {
        'breadcrumbs': breadcrumbs,
        'oll_groups': oll_groups,
        'two_look_oll': two_look_oll,
        'tips': tips,
        'total_oll_cases': 57,
        'two_look_count': 10,
    }
    
    return render(request, 'francontcube/methods/cfop/oll_intro.html', context)