"""
Step 2: F2L (First Two Layers) - CFOP Method
"""

from ..base import StepView
from cube.models import CubeState  # ← Changed from francontcube.models
from collections import OrderedDict
from django.shortcuts import render

import json  # ← Make sure this line is there!

class F2LView(StepView):
    """
    Step 2: First Two Layers - CFOP Method.
    
    Solve 4 corner-edge pairs simultaneously to complete the first two layers.
    This is the most intuitive step in CFOP but requires practice for speed.
    """
    
    template_name = "francontcube/methods/cfop/f2l.html"
    method_name = "CFOP"
    step_name = "F2L"
    step_number = 2
    step_icon = "layers"
    
    # Navigation
    next_step = "francontcube:cfop_oll"
    prev_step = "francontcube:cfop_cross"
    
    # Cube states - we'll add F2L cases later
    cube_state_slugs = {
        'goal_state': 'cfop-f2l-goal',
    }


# Export
f2l = F2LView.as_view()


def cfop(request):
    """CFOP method overview page"""
    
    steps = [
        {
            'name': 'À propos de CFOP',
            'desc': 'Découvrez la méthode CFOP et ses avantages',
            'icon': 'bi bi-info-circle',
            'url': '/cfop/about/',
            'available': True,
            'step_number': None,
        },
        {
            'name': 'Cross (Croix)',
            'desc': 'Former la croix blanche en moins de 8 mouvements',
            'icon': 'bi bi-plus-lg',
            'url': '#',
            'available': False,
            'step_number': 1,
        },
        {
            'name': 'F2L (First Two Layers)',
            'desc': 'Insérer les 4 paires coin-arête simultanément',
            'icon': 'bi bi-layers',
            'url': '/cfop/f2l/basic/',
            'available': True,
            'step_number': 2,
        },
        {
            'name': 'OLL (Orient Last Layer)',
            'desc': 'Orienter la dernière couche (57 cas)',
            'icon': 'bi bi-sun',
            'url': '#',
            'available': False,
            'step_number': 3,
        },
        {
            'name': 'PLL (Permute Last Layer)',
            'desc': 'Permuter la dernière couche (21 cas)',
            'icon': 'bi bi-shuffle',
            'url': '#',
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
    
    return render(request, 'francontcube/methods/cfop/index.html', context)


def cfop_f2l_basic(request):
    """Display the first 4 basic F2L cases"""
    
    slugs = ['f2l1', 'f2l2', 'f2l3', 'f2l4']
    cube_states = OrderedDict()
    
    for slug in slugs:
        try:
            cube_states[slug] = CubeState.objects.get(slug=slug)
            print(f"✓ Found {slug}")  # Debug
        except CubeState.DoesNotExist:
            cube_states[slug] = None
            print(f"✗ Missing {slug}")  # Debug
    
    # Prepare cube states for JavaScript
    cube_states_json = {}
    for slug, state in cube_states.items():
        if state and state.json_state:
            cube_states_json[slug] = {
                'json_state': state.json_state,
                'json_highlight': state.json_highlight if state.json_highlight else {},
            }
            print(f"✓ Added {slug} to json")  # Debug
        else:
            cube_states_json[slug] = None
            print(f"✗ Skipped {slug} (no state or json_state)")  # Debug
    
    json_string = json.dumps(cube_states_json)
    print(f"\n=== JSON String Length: {len(json_string)} ===")  # Debug
    print(f"First 100 chars: {json_string[:100]}")  # Debug
    
    context = {
        'cube_states': cube_states,
        'cube_states_json': json_string,
        'page_title': 'F2L - Cas de Base',
    }
    
    print(f"\n=== Context keys: {context.keys()} ===")  # Debug
    print(f"cube_states_json in context: {'cube_states_json' in context}")  # Debug
    
    return render(request, 'francontcube/methods/cfop/f2l_basic.html', context)