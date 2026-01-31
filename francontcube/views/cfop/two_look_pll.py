# francontcube/views/cfop/two_look_pll.py
"""
2-Look PLL - Beginner-friendly approach to PLL
Only 6 cases to learn instead of 21!

Step 1: Permute Corners - 2 cases
Step 2: Permute Edges - 4 cases
"""

from django.shortcuts import render

# 2-Look PLL Case Groups
TWO_LOOK_PLL_CASES = {
    'step1': {
        'name': 'Étape 1 : Permutation des Coins',
        'description': 'Placer tous les coins à la bonne position. Seulement 2 motifs à reconnaître!',
        'icon': 'bi-diamond',
        'color': 'primary',
        'cases': [
            {
                'slug': 'pll-adjacent-corners',
                'name': 'Coins Adjacents',
                'pattern': '2 coins côte à côte',
                'algorithm': "x R' U R' D2 R U' R' D2 R2 x'",
                'recognition': 'Deux coins sur la même face doivent être échangés',
                'note': 'Aussi appelé Aa-perm. Positionner les coins résolus à l\'arrière.',
            },
            {
                'slug': 'pll-diagonal-corners',
                'name': 'Coins Diagonaux',
                'pattern': '2 coins en diagonale',
                'algorithm': "F R U' R' U' R U R' F' R U R' U' R' F R F'",
                'recognition': 'Les coins en diagonale opposée doivent être échangés',
                'note': 'Aussi appelé Y-perm. Peut être fait de n\'importe quel angle.',
            },
        ]
    },
    'step2': {
        'name': 'Étape 2 : Permutation des Arêtes',
        'description': 'Placer toutes les arêtes à la bonne position. 4 motifs - tous basés sur les U-perms!',
        'icon': 'bi-arrows-move',
        'color': 'success',
        'cases': [
            {
                'slug': 'pll-three-edge-cycle',
                'name': 'Cycle de 3 Arêtes (Ua)',
                'pattern': '3 arêtes doivent tourner',
                'algorithm': "R U' R U R U R U' R' U' R2",
                'recognition': 'Une arête résolue, trois doivent cycler',
                'note': 'Positionner l\'arête résolue à l\'arrière. Pour le sens antihoraire, utiliser Ub.',
            },
            {
                'slug': 'pll-opposite-edges',
                'name': 'Arêtes Opposées (H)',
                'pattern': '2 paires d\'arêtes opposées',
                'algorithm': "M2 U M2 U2 M2 U M2",
                'recognition': 'Les deux paires opposées doivent être échangées',
                'note': 'Facile à reconnaître - motif damier sur les côtés.',
            },
            {
                'slug': 'pll-adjacent-edges',
                'name': 'Arêtes Adjacentes (Z)',
                'pattern': '2 paires d\'arêtes adjacentes',
                'algorithm': "M' U M2 U M2 U M' U2 M2",
                'recognition': 'Deux paires adjacentes doivent être échangées',
                'note': 'Positionner une paire résolue à l\'arrière.',
            },
            {
                'slug': 'pll-solved',
                'name': 'Résolu!',
                'pattern': 'Toutes les arêtes correctes',
                'algorithm': '',
                'recognition': 'Le cube est complet!',
                'note': 'Félicitations! 🎉',
            },
        ]
    }
}


def two_look_pll_view(request):
    """
    Display 2-Look PLL teaching page with steps and cases.
    """
    from cube.two_look_pll_patterns import get_two_look_pll_pattern
    
    # Add SVG patterns to each case
    step1_cases = TWO_LOOK_PLL_CASES['step1']['cases']
    step2_cases = TWO_LOOK_PLL_CASES['step2']['cases']
    
    # Convert patterns to template format for each case
    for case in step1_cases:
        pattern_key = case['slug'].replace('pll-', '')
        raw_pattern = get_two_look_pll_pattern(pattern_key)
        if raw_pattern:
            case['pattern_data'] = _convert_pattern_to_template_format(raw_pattern)
    
    for case in step2_cases:
        pattern_key = case['slug'].replace('pll-', '')
        raw_pattern = get_two_look_pll_pattern(pattern_key)
        if raw_pattern:
            case['pattern_data'] = _convert_pattern_to_template_format(raw_pattern)
    
    context = {
        'page_title': '2-Look PLL - Méthode CFOP',
        'page_description': 'Maîtrisez PLL en seulement 6 algorithmes! La façon la plus simple de compléter la dernière couche.',
        'step1': TWO_LOOK_PLL_CASES['step1'],
        'step2': TWO_LOOK_PLL_CASES['step2'],
        'total_algorithms': 6,
    }
    
    return render(request, 'francontcube/methods/cfop/two_look_pll.html', context)


def _convert_pattern_to_template_format(pattern):
    """
    Convert pattern dict to template-friendly format.
    
    Args:
        pattern: Raw pattern from two_look_pll_patterns.py
    
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
            '0': pattern.get('F', [' #00D800'] * 3)[0],
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