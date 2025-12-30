# francontcube/views/cfop/f2l.py

from django.shortcuts import render
from django.urls import reverse
from cube.models import CubeState
from collections import OrderedDict
import json

# F2L Categories definition
F2L_CATEGORIES = {
    'basic': {
        'name': 'Cas de Base',
        'description': 'Les 4 premiers cas F2L - Paires déjà formées',
        'slug_range': range(1, 5),  # f2l-01 to f2l-04
        'icon': 'bi-star-fill',
        'color': 'success'
    },
    'corner-right-edge-right': {
        'name': 'Coin Droite, Arête Droite',
        'description': 'Les deux pièces sur le même côté (droite)',
        'slug_range': range(5, 9),  # f2l-05 to f2l-08
        'icon': 'bi-arrow-right',
        'color': 'primary'
    },
    'corner-right-edge-front': {
        'name': 'Coin Droite, Arête Devant',
        'description': 'Pièces sur des côtés différents',
        'slug_range': range(9, 13),  # f2l-09 to f2l-12
        'icon': 'bi-arrows',
        'color': 'info'
    },
    'corner-left-edge-left': {
        'name': 'Coin Gauche, Arête Gauche',
        'description': 'Miroir des cas 5-8 (côté gauche)',
        'slug_range': range(13, 17),  # f2l-13 to f2l-16
        'icon': 'bi-arrow-left',
        'color': 'primary'
    },
    'corner-left-edge-front': {
        'name': 'Coin Gauche, Arête Devant',
        'description': 'Miroir des cas 9-12',
        'slug_range': range(17, 21),  # f2l-17 to f2l-20
        'icon': 'bi-arrows',
        'color': 'info'
    },
    'corner-in-slot': {
        'name': 'Coin dans le Slot',
        'description': 'Le coin est déjà inséré (mal orienté)',
        'slug_range': range(21, 29),  # f2l-21 to f2l-28
        'icon': 'bi-box-arrow-down',
        'color': 'warning'
    },
    'edge-in-slot': {
        'name': 'Arête dans le Slot',
        'description': "L'arête est déjà insérée (mal orientée)",
        'slug_range': range(29, 37),  # f2l-29 to f2l-36
        'icon': 'bi-box-arrow-up',
        'color': 'warning'
    },
    'both-in-slot': {
        'name': 'Les Deux dans le Slot',
        'description': 'Cas difficiles - les deux pièces sont mal placées',
        'slug_range': range(37, 42),  # f2l-37 to f2l-41
        'icon': 'bi-exclamation-triangle',
        'color': 'danger'
    },
}


def cfop(request):
    """CFOP method overview page"""
    
    steps = [
        {
            'name': 'À propos de CFOP',
            'desc': 'Découvrez la méthode CFOP et ses avantages',
            'icon': 'bi bi-info-circle',
            'url': reverse('francontcube:cfop_about'),
            'available': True,
            'step_number': None,
        },
        {
            'name': 'Cross (Croix)',
            'desc': 'Former la croix blanche en moins de 8 mouvements',
            'icon': 'bi bi-plus-lg',
            'url': reverse('francontcube:cfop_cross'),
            'available': False,
            'step_number': 1,
        },
        {
            'name': 'F2L (First Two Layers)',
            'desc': 'Insérer les 4 paires coin-arête simultanément',
            'icon': 'bi bi-layers',
            'url': reverse('francontcube:cfop_f2l_basic'),
            'available': True,
            'step_number': 2,
        },
        {
            'name': 'OLL (Orient Last Layer)',
            'desc': 'Orienter la dernière couche (57 cas)',
            'icon': 'bi bi-sun',
            'url': reverse('francontcube:cfop_oll'),
            'available': False,
            'step_number': 3,
        },
        {
            'name': 'PLL (Permute Last Layer)',
            'desc': 'Permuter la dernière couche (21 cas)',
            'icon': 'bi bi-shuffle',
            'url': reverse('francontcube:cfop_pll'),
            'available': False,
            'step_number': 4,
        },
    ]
    
    context = {
        'method_name': 'CFOP (Méthode Fridrich)',
        'method_description': 'La méthode de speedcubing la plus populaire au monde',
        'difficulty': 'Avancé',
        'estimated_time': '3-6 mois',
        'total_steps': 4,
        'algorithms_count': '78+ algorithmes',
        'steps': steps,
    }
    
    return render(request, 'francontcube/cfop/index.html', context)


def cfop_f2l_basic(request, category=None):
    """Display F2L cases, optionally filtered by category"""
    
    # Get all F2L cases
    all_cases = CubeState.objects.filter(method='cfop', slug__startswith='f2l-').order_by('step_number')
    
    # Determine which slugs to show
    if category and category in F2L_CATEGORIES:
        # Filter by category
        cat_info = F2L_CATEGORIES[category]
        slug_nums = cat_info['slug_range']
        slugs = [f'f2l-{num:02d}' for num in slug_nums]
        page_title = cat_info['name']
        page_description = cat_info['description']
    else:
        # Show basic cases by default (you can change this to show all or any category)
        slugs = ['f2l-01', 'f2l-02', 'f2l-03', 'f2l-04']
        page_title = 'F2L - Cas de Base'
        page_description = 'Les 4 premiers cas F2L (First Two Layers) - Paires déjà formées'
    
    # Build ordered dictionary of cube states (your existing logic)
    cube_states = OrderedDict()
    for slug in slugs:
        try:
            cube_states[slug] = CubeState.objects.get(slug=slug)
        except CubeState.DoesNotExist:
            cube_states[slug] = None
    
    # Prepare cube states for JavaScript (your existing logic)
    cube_states_json = {}
    for slug, state in cube_states.items():
        if state and state.json_state:
            cube_states_json[slug] = {
                'json_state': state.json_state,
                'json_highlight': state.json_highlight if state.json_highlight else {},
            }
        else:
            cube_states_json[slug] = None
    
    json_string = json.dumps(cube_states_json)
    
    # Prepare category navigation
    categories_nav = []
    for cat_key, cat_data in F2L_CATEGORIES.items():
        categories_nav.append({
            'key': cat_key,
            'name': cat_data['name'],
            'description': cat_data['description'],
            'icon': cat_data['icon'],
            'color': cat_data['color'],
            'url': reverse('francontcube:cfop_f2l_category', kwargs={'category': cat_key}),
            'active': cat_key == category,
            'count': len(list(cat_data['slug_range']))
        })
    
    context = {
        'cube_states': cube_states,
        'cube_states_json': json_string,
        'page_title': page_title,
        'page_description': page_description,
        'current_category': category,
        'categories': categories_nav,
        'total_cases': all_cases.count(),
    }
    
    return render(request, 'francontcube/methods/cfop/f2l_basic.html', context)

    

def my_custom_view(request):
    # Récupérer tous les cas difficiles
    difficult_cases = CubeState.objects.filter(
        method='cfop',
        difficulty='difficile'
    ).order_by('step_number')
    
    # Ou filtrer par plusieurs catégories
    slot_cases = CubeState.objects.filter(
        method='cfop',
        category__in=['corner-in-slot', 'edge-in-slot']
    )
    
    return render(request, 'template.html', {
        'difficult_cases': difficult_cases,
        'slot_cases': slot_cases,
    })