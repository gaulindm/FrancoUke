"""
F2L Introduction page - Detailed explanation of the F2L step.

This page explains:
- What is F2L and why it's important
- The 8 categories of F2L cases
- Tips and strategies
- How to practice efficiently
"""

from django.shortcuts import render
from django.urls import reverse
from cube.models import CubeState


def cfop_f2l_intro(request):
    """
    Introduction page for F2L (First Two Layers).
    
    Provides detailed explanation before users access the 41 cases.
    """
    breadcrumbs = [
        {'name': 'Accueil', 'url': reverse('francontcube:home')},
        {'name': 'CFOP', 'url': reverse('francontcube:method_cfop')},
        {'name': 'F2L - Introduction', 'url': ''},
    ]
    
    # Categories with their details
    f2l_categories = [
        {
            'slug': 'basic',
            'name': 'Cas de Base',
            'icon': 'bi-star-fill',
            'color': 'success',
            'cases_count': 4,
            'difficulty': 'Facile',
            'description': 'La paire coin-arête est déjà formée, il suffit de l\'insérer dans le slot.',
            'key_concept': 'Insertion simple',
            'example_alg': 'R U R\'',
        },
        {
            'slug': 'corner-right-edge-right',
            'name': 'Coin Droite, Arête Droite',
            'icon': 'bi-arrow-right-square',
            'color': 'primary',
            'cases_count': 4,
            'difficulty': 'Moyen',
            'description': 'Le coin et l\'arête sont du même côté (droite), il faut les séparer puis réunir.',
            'key_concept': 'Séparation puis réunion',
            'example_alg': 'U R U\' R\' U\' F\' U F',
        },
        {
            'slug': 'corner-right-edge-front',
            'name': 'Coin Droite, Arête Devant',
            'icon': 'bi-arrow-down-right-square',
            'color': 'info',
            'cases_count': 4,
            'difficulty': 'Moyen',
            'description': 'Le coin est à droite et l\'arête devant. Nécessite une approche en deux temps.',
            'key_concept': 'Positionnement puis insertion',
            'example_alg': 'U\' R U\' R\' U2 F\' U\' F',
        },
        {
            'slug': 'corner-left-edge-left',
            'name': 'Coin Gauche, Arête Gauche',
            'icon': 'bi-arrow-left-square',
            'color': 'primary',
            'cases_count': 4,
            'difficulty': 'Moyen',
            'description': 'Version miroir du cas 2. Même logique mais avec la main gauche.',
            'key_concept': 'Miroir main gauche',
            'example_alg': 'U\' L\' U L U F U\' F\'',
        },
        {
            'slug': 'corner-left-edge-front',
            'name': 'Coin Gauche, Arête Devant',
            'icon': 'bi-arrow-down-left-square',
            'color': 'info',
            'cases_count': 4,
            'difficulty': 'Moyen',
            'description': 'Version miroir du cas 3. Le coin gauche avec arête devant.',
            'key_concept': 'Miroir avec timing',
            'example_alg': 'U L\' U L U2 F U F\'',
        },
        {
            'slug': 'corner-in-slot',
            'name': 'Coin dans le Slot',
            'icon': 'bi-box-arrow-in-down-right',
            'color': 'warning',
            'cases_count': 8,
            'difficulty': 'Facile à Moyen',
            'description': 'Le coin est déjà dans le slot (mal orienté). L\'arête est en haut.',
            'key_concept': 'Extraction puis réinsertion',
            'example_alg': 'R U\' R\' U R U\' R\'',
        },
        {
            'slug': 'edge-in-slot',
            'name': 'Arête dans le Slot',
            'icon': 'bi-box-arrow-in-down',
            'color': 'warning',
            'cases_count': 8,
            'difficulty': 'Facile à Moyen',
            'description': 'L\'arête est dans le slot (mal orientée). Le coin est en haut.',
            'key_concept': 'Cacher puis révéler',
            'example_alg': 'U\' R U R\' U\' R U R\'',
        },
        {
            'slug': 'both-in-slot',
            'name': 'Les Deux dans le Slot',
            'icon': 'bi-exclamation-triangle-fill',
            'color': 'danger',
            'cases_count': 5,
            'difficulty': 'Difficile',
            'description': 'Les deux pièces sont mal placées dans le slot. Cas les plus complexes.',
            'key_concept': 'Algorithmes avancés',
            'example_alg': 'R U\' R\' U\' R U R\' U2 R U\' R\'',
        },
    ]
    
    # Learning progression
    learning_path = [
        {
            'step': 1,
            'title': 'Maîtriser les 4 cas de base',
            'desc': 'Commencez par les insertions simples pour comprendre le concept.',
            'time': '1-2 jours',
            'cases': 'F2L #1-4',
        },
        {
            'step': 2,
            'title': 'Apprendre les cas "coin dans slot"',
            'desc': 'Ces 8 cas sont fréquents et utilisent le célèbre "Sexy Move".',
            'time': '3-5 jours',
            'cases': 'F2L #21-28',
        },
        {
            'step': 3,
            'title': 'Ajouter les cas simples séparés',
            'desc': 'Coin et arête du même côté, faciles à reconnaître.',
            'time': '1 semaine',
            'cases': 'F2L #5-8, #13-16',
        },
        {
            'step': 4,
            'title': 'Apprendre les cas croisés',
            'desc': 'Coin d\'un côté, arête devant. Plus de setup requis.',
            'time': '1-2 semaines',
            'cases': 'F2L #9-12, #17-20',
        },
        {
            'step': 5,
            'title': 'Maîtriser "arête dans slot"',
            'desc': 'L\'arête est insérée, il faut positionner le coin correctement.',
            'time': '1 semaine',
            'cases': 'F2L #29-36',
        },
        {
            'step': 6,
            'title': 'Cas difficiles final boss',
            'desc': 'Les 5 cas les plus complexes. Patience et répétition!',
            'time': '1-2 semaines',
            'cases': 'F2L #37-41',
        },
    ]
    
    # Key tips
    tips = [
        {
            'icon': 'bi-eye',
            'title': 'Reconnaissance Visuelle',
            'desc': 'Identifiez d\'abord OÙ sont les pièces (haut, slot), puis COMMENT elles sont orientées (blanc dessus, côté).',
        },
        {
            'icon': 'bi-lightning',
            'title': 'Pas de Rotation de Cube',
            'desc': 'Apprenez les algorithmes miroirs (main gauche) plutôt que de tourner tout le cube.',
        },
        {
            'icon': 'bi-repeat',
            'title': 'Le Sexy Move est Roi',
            'desc': 'R U R\' U\' est la base de nombreux cas. Maîtrisez-le parfaitement.',
        },
        {
            'icon': 'bi-graph-up',
            'title': 'Pratiquez Lentement',
            'desc': 'La vitesse viendra naturellement. Concentrez-vous d\'abord sur la fluidité.',
        },
        {
            'icon': 'bi-bullseye',
            'title': 'Look Ahead',
            'desc': 'Pendant une paire, cherchez déjà la prochaine. C\'est la clé du sub-20.',
        },
        {
            'icon': 'bi-bookmark-star',
            'title': 'Cas Favoris',
            'desc': 'Chaque cubeur a des algorithmes préférés. N\'hésitez pas à adapter selon votre style.',
        },
    ]
    
    # Statistics
    total_cases = CubeState.objects.filter(method='cfop', category__isnull=False).count()
    easy_cases = CubeState.objects.filter(method='cfop', difficulty='facile').count()
    medium_cases = CubeState.objects.filter(method='cfop', difficulty='moyen').count()
    hard_cases = CubeState.objects.filter(method='cfop', difficulty='difficile').count()
    
    context = {
        'breadcrumbs': breadcrumbs,
        'f2l_categories': f2l_categories,
        'learning_path': learning_path,
        'tips': tips,
        'total_cases': total_cases,
        'easy_cases': easy_cases,
        'medium_cases': medium_cases,
        'hard_cases': hard_cases,
    }
    
    return render(request, 'francontcube/methods/cfop/f2l_intro.html', context)