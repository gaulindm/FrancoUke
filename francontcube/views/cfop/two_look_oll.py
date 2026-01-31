# francontcube/views/cfop/two_look_oll.py
"""
2-Look OLL - Beginner-friendly approach to OLL
Only 10 cases to learn instead of 57!

Step 1: Orient Edges (Yellow Cross) - 3 cases
Step 2: Orient Corners (Yellow Face) - 7 cases
"""

from django.shortcuts import render
from cube.models import CubeState

# 2-Look OLL Case Groups
TWO_LOOK_OLL_CASES = {
    'step1': {
        'name': 'Étape 1 : Croix Jaune',
        'description': 'Orienter les arêtes pour former une croix jaune sur le dessus. Seulement 3 motifs à apprendre!',
        'icon': 'bi-plus-lg',
        'color': 'warning',
        'cases': [
            {
                'slug': 'oll-dot-cross',
                'name': 'Point → Croix',
                'pattern': 'Aucune arête orientée',
                'algorithm': "F R U R' U' F'",
                'recognition': 'Aucune arête jaune sur le dessus',
            },
            {
                'slug': 'oll-line-cross', 
                'name': 'Ligne → Croix',
                'pattern': 'Ligne de 2 arêtes',
                'algorithm': "F R U R' U' F'",
                'recognition': 'Ligne horizontale de jaune',
            },
            {
                'slug': 'oll-l-cross',
                'name': 'Forme L → Croix', 
                'pattern': 'Forme L de 2 arêtes',
                'algorithm': "F U R U' R' F'",
                'recognition': 'Forme L à gauche',
            },
        ]
    },
    'step2': {
        'name': 'Étape 2 : Face Jaune',
        'description': 'Orienter tous les coins pour completer la face jaune. 7 cas basés sur Sune et Anti-Sune.',
        'icon': 'bi-square-fill',
        'color': 'success',
        'cases': [
            {
                'slug': 'oll-sune',
                'name': 'Sune',
                'pattern': '1 coin orienté',
                'algorithm': "R U R' U R U2 R'",
                'recognition': 'Motif poisson - phares à droite',
            },
            {
                'slug': 'oll-antisune',
                'name': 'Anti-Sune',
                'pattern': '1 coin orienté',
                'algorithm': "R U2 R' U' R U' R'",
                'recognition': 'Motif poisson - phares à gauche',
            },
            {
                'slug': 'oll-h-pattern',
                'name': 'Motif H',
                'pattern': '2 coins opposés',
                'algorithm': "R U R' U R U' R' U R U2 R'",
                'recognition': 'Motif damier',
            },
            {
                'slug': 'oll-pi-pattern',
                'name': 'Motif Pi',
                'pattern': '2 coins adjacents',
                'algorithm': "R U2 R2 U' R2 U' R2 U2 R",
                'recognition': 'Deux phares devant',
            },
            {
                'slug': 'oll-u-pattern',
                'name': 'Motif U',
                'pattern': '2 coins adjacents',
                'algorithm': "R2 D R' U2 R D' R' U2 R'",
                'recognition': 'Forme U face à vous',
            },
            {
                'slug': 'oll-t-pattern',
                'name': 'Motif T',
                'pattern': '2 coins adjacents',
                'algorithm': "r U R' U' r' F R F'",
                'recognition': 'Forme T devant',
            },
            {
                'slug': 'oll-l-pattern',
                'name': 'Motif L',
                'pattern': '2 coins adjacents',
                'algorithm': "F R' F' r U R U' r'",
                'recognition': 'Forme L dans le coin',
            },
        ]
    }
}


def two_look_oll_view(request):
    """
    Display 2-Look OLL teaching page with steps and cases.
    """
    from cube.two_look_oll_patterns import get_two_look_oll_pattern
    
    # Add SVG patterns to each case
    step1_cases = TWO_LOOK_OLL_CASES['step1']['cases']
    step2_cases = TWO_LOOK_OLL_CASES['step2']['cases']
    
    # Convert patterns to template format for each case
    for case in step1_cases:
        pattern_key = case['slug'].replace('oll-', '').replace('-cross', '-cross')
        raw_pattern = get_two_look_oll_pattern(pattern_key)
        if raw_pattern:
            case['pattern_data'] = _convert_pattern_to_template_format(raw_pattern)
    
    for case in step2_cases:
        pattern_key = case['slug'].replace('oll-', '')
        raw_pattern = get_two_look_oll_pattern(pattern_key)
        if raw_pattern:
            case['pattern_data'] = _convert_pattern_to_template_format(raw_pattern)
    
    context = {
        'page_title': '2-Look OLL - Méthode CFOP',
        'page_description': 'Maîtrisez OLL en seulement 10 algorithmes! Parfait pour les débutants qui passent de 4LLL au CFOP complet.',
        'step1': TWO_LOOK_OLL_CASES['step1'],
        'step2': TWO_LOOK_OLL_CASES['step2'],
        'total_algorithms': 10,
    }
    
    return render(request, 'francontcube/methods/cfop/two_look_oll.html', context)


def _convert_pattern_to_template_format(pattern):
    """
    Convert pattern dict to template-friendly format.
    
    Args:
        pattern: Raw pattern from two_look_oll_patterns.py
    
    Returns:
        dict: Template-formatted pattern with nested dicts
    """
    return {
        'U': {
            '0': {
                '0': pattern['U'][0][0],
                '1': pattern['U'][0][1],
                '2': pattern['U'][0][2],
            },
            '1': {
                '0': pattern['U'][1][0],
                '1': pattern['U'][1][1],
                '2': pattern['U'][1][2],
            },
            '2': {
                '0': pattern['U'][2][0],
                '1': pattern['U'][2][1],
                '2': pattern['U'][2][2],
            },
        },
        'F': {
            '0': pattern.get('F', ['#00D800'] * 3)[0],
            '1': pattern.get('F', ['#00D800'] * 3)[1],
            '2': pattern.get('F', ['#00D800'] * 3)[2],
        },
        'R': {
            '0': pattern.get('R', ['#C41E3A'] * 3)[0],
            '1': pattern.get('R', ['#C41E3A'] * 3)[1],
            '2': pattern.get('R', ['#C41E3A'] * 3)[2],
        },
        'B': {
            '0': pattern.get('B', ['#0051BA'] * 3)[0],
            '1': pattern.get('B', ['#0051BA'] * 3)[1],
            '2': pattern.get('B', ['#0051BA'] * 3)[2],
        },
        'L': {
            '0': pattern.get('L', ['#FF5800'] * 3)[2],  # Reversed
            '1': pattern.get('L', ['#FF5800'] * 3)[1],
            '2': pattern.get('L', ['#FF5800'] * 3)[0],  # Reversed
        },
    }