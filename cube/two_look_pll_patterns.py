# cube/two_look_pll_patterns.py
"""
2-Look PLL Pattern Definitions for SVG visualization.

Step 1: Corner Permutation (2 cases)
Step 2: Edge Permutation (4 cases)

These use simplified patterns for teaching purposes.
For PLL, the U face is always all white (everything oriented),
but the side colors show which pieces are swapped.
"""

# Color constants
WHITE  = '#FFFFFF'  # Top face (toujours blanc pour PLL)
GREEN  = '#00D800'  # Front face
RED    = '#C41E3A'  # Right face
BLUE   = '#0051BA'  # Back face
ORANGE = '#FF5800'  # Left face

# All white top face (used in all PLL cases)
ALL_WHITE = [
    [WHITE, WHITE, WHITE],
    [WHITE, WHITE, WHITE],
    [WHITE, WHITE, WHITE],
]

# ============================================================================
# 2-LOOK PLL PATTERNS
# ============================================================================

TWO_LOOK_PLL_PATTERNS = {
    # ========================================
    # STEP 1: Corner Permutation
    # ========================================
    
    'adjacent-corners': {
        'name': 'Coins Adjacents (Aa/Ab)',
        'step': 1,
        'description': 'Échanger deux coins adjacents - utiliser Aa ou Ab perm',
        'U': ALL_WHITE,
        'F': [GREEN,  GREEN,  ORANGE],
        'R': [RED,    RED,    RED],
        'B': [BLUE,   BLUE,   BLUE],
        'L': [GREEN,  ORANGE, ORANGE],
    },
    
    'diagonal-corners': {
        'name': 'Coins Diagonaux (Y/E)',
        'step': 1,
        'description': 'Échanger deux coins diagonaux - utiliser Y perm ou E perm',
        'U': ALL_WHITE,
        'F': [GREEN,  GREEN,  ORANGE],
        'R': [RED,    RED,    RED],
        'B': [GREEN,  BLUE,   BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    
    # ========================================
    # STEP 2: Edge Permutation (after corners are solved)
    # ========================================
    
    'three-edge-cycle': {
        'name': 'Cycle de 3 Arêtes (Ua/Ub)',
        'step': 2,
        'description': 'Cycler 3 arêtes - utiliser Ua ou Ub perm',
        'U': ALL_WHITE,
        'F': [GREEN,  RED,    GREEN],
        'R': [RED,    BLUE,   RED],
        'B': [BLUE,   GREEN,  BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    
    'opposite-edges': {
        'name': 'Arêtes Opposées (H)',
        'step': 2,
        'description': 'Échanger les paires opposées - utiliser H perm',
        'U': ALL_WHITE,
        'F': [GREEN,  BLUE,   GREEN],
        'R': [RED,    ORANGE, RED],
        'B': [BLUE,   GREEN,  BLUE],
        'L': [ORANGE, RED,    ORANGE],
    },
    
    'adjacent-edges': {
        'name': 'Arêtes Adjacentes (Z)',
        'step': 2,
        'description': 'Échanger les paires adjacentes - utiliser Z perm',
        'U': ALL_WHITE,
        'F': [GREEN,  RED,    GREEN],
        'R': [RED,    GREEN,  RED],
        'B': [BLUE,   ORANGE, BLUE],
        'L': [ORANGE, BLUE,   ORANGE],
    },
    
    'solved': {
        'name': 'Résolu !',
        'step': 2,
        'description': 'Toutes les pièces au bon endroit - cube résolu !',
        'U': ALL_WHITE,
        'F': [GREEN,  GREEN,  GREEN],
        'R': [RED,    RED,    RED],
        'B': [BLUE,   BLUE,   BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
}


def get_two_look_pll_pattern(pattern_key):
    """
    Get 2-Look PLL pattern by key.
    """
    return TWO_LOOK_PLL_PATTERNS.get(pattern_key)


def get_step_patterns(step_number):
    """
    Get all patterns for a specific step.
    """
    return {
        key: pattern 
        for key, pattern in TWO_LOOK_PLL_PATTERNS.items() 
        if pattern['step'] == step_number
    }


def list_all_two_look_pll_patterns():
    """Return list of all 2-Look PLL pattern keys"""
    return list(TWO_LOOK_PLL_PATTERNS.keys())