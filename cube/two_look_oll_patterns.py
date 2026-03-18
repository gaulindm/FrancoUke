# cube/two_look_oll_patterns.py
"""
2-Look OLL Pattern Definitions for SVG visualization.

Step 1: Cross patterns (3 cases)
Step 2: Corner patterns (7 cases)

These use simplified patterns for teaching purposes.
"""

# Color constants
WHITE  = '#FFFFFF'  # Oriented (face du haut = blanc)
GRAY   = '#808080'  # Not oriented
GREEN  = '#00D800'  # Front (default)
RED    = '#C41E3A'  # Right (default)
BLUE   = '#0051BA'  # Back (default)
ORANGE = '#FF5800'  # Left (default)

# ============================================================================
# 2-LOOK OLL PATTERNS
# ============================================================================

TWO_LOOK_OLL_PATTERNS = {
    # ========================================
    # STEP 1: White Cross (Edge Orientation)
    # ========================================
    
    'dot-cross': {
        'name': 'Point → Croix',
        'step': 1,
        'description': 'Aucune arête orientée - faire une croix blanche',
        'U': [
            [GRAY,  GRAY,  GRAY],
            [GRAY,  WHITE, GRAY],
            [GRAY,  GRAY,  GRAY],
        ],
        'F': [GRAY, WHITE, GRAY],
        'R': [GRAY, WHITE, GRAY],
        'B': [GRAY, WHITE, GRAY],
        'L': [GRAY, WHITE, GRAY],
    },
    
    'line-cross': {
        'name': 'Ligne → Croix',
        'step': 1,
        'description': 'Ligne horizontale de 2 arêtes',
        'U': [
            [GRAY,  GRAY,  GRAY],
            [WHITE, WHITE, WHITE],
            [GRAY,  GRAY,  GRAY],
        ],
        'F': [GRAY, WHITE, GRAY],
        'R': [GRAY, GRAY,  GRAY],
        'B': [GRAY, WHITE, GRAY],
        'L': [GRAY, GRAY,  GRAY],
    },
    
    'l-cross': {
        'name': 'Forme L → Croix',
        'step': 1,
        'description': 'Forme L blanche à gauche',
        'U': [
            [GRAY, GRAY,  GRAY],
            [GRAY, WHITE, WHITE],
            [GRAY, WHITE, GRAY],
        ],
        'F': [GRAY, GRAY,  GRAY],
        'R': [GRAY, GRAY,  GRAY],
        'B': [GRAY, WHITE, GRAY],
        'L': [GRAY, WHITE, GRAY],
    },
    
    # ========================================
    # STEP 2: White Face (Corner Orientation)
    # After cross is done, U face edges are all white
    # ========================================
    
    'sune': {
        'name': 'Sune',
        'step': 2,
        'description': 'Motif poisson - phares à droite',
        'U': [
            [GRAY,  WHITE, GRAY],
            [WHITE, WHITE, WHITE],
            [WHITE, WHITE, GRAY],
        ],
        'F': [GRAY,  GRAY, WHITE],
        'R': [WHITE, GRAY, GRAY],
        'B': [WHITE, GRAY, GRAY],
        'L': [GRAY,  GRAY, GRAY],
    },
    
    'antisune': {
        'name': 'Anti-Sune',
        'step': 2,
        'description': 'Motif poisson - phares à gauche',
        'U': [
            [GRAY,  WHITE, GRAY],
            [WHITE, WHITE, WHITE],
            [GRAY,  WHITE, WHITE],
        ],
        'F': [WHITE, GRAY, GRAY],
        'R': [GRAY,  GRAY, GRAY],
        'B': [GRAY,  GRAY, WHITE],
        'L': [WHITE, GRAY, GRAY],
    },
    
    'h-pattern': {
        'name': 'Motif H',
        'step': 2,
        'description': 'Motif damier - 2 coins opposés',
        'U': [
            [GRAY,  WHITE, GRAY],
            [WHITE, WHITE, WHITE],
            [GRAY,  WHITE, GRAY],
        ],
        'F': [GRAY,  GRAY, GRAY],
        'R': [WHITE, GRAY, WHITE],
        'B': [GRAY,  GRAY, GRAY],
        'L': [WHITE, GRAY, WHITE],
    },
    
    'pi-pattern': {
        'name': 'Motif Pi',
        'step': 2,
        'description': 'Deux phares devant',
        'U': [
            [GRAY,  WHITE, GRAY],
            [WHITE, WHITE, WHITE],
            [GRAY,  WHITE, GRAY],
        ],
        'F': [GRAY,  GRAY, WHITE],
        'R': [GRAY,  GRAY, GRAY],
        'B': [GRAY,  GRAY, WHITE],
        'L': [WHITE, GRAY, WHITE],
    },
    
    'u-pattern': {
        'name': 'Motif U',
        'step': 2,
        'description': 'Forme U face à vous',
        'U': [
            [WHITE, WHITE, WHITE],
            [WHITE, WHITE, WHITE],
            [GRAY,  WHITE, GRAY],
        ],
        'F': [WHITE, GRAY, WHITE],
        'R': [GRAY,  GRAY, GRAY],
        'B': [GRAY,  GRAY, GRAY],
        'L': [GRAY,  GRAY, GRAY],
    },
    
    't-pattern': {
        'name': 'Motif T',
        'step': 2,
        'description': 'Forme T devant',
        'U': [
            [GRAY,  WHITE, WHITE],
            [WHITE, WHITE, WHITE],
            [GRAY,  WHITE, WHITE],
        ],
        'F': [WHITE, GRAY, GRAY],
        'R': [GRAY,  GRAY, GRAY],
        'B': [WHITE, GRAY, GRAY],
        'L': [GRAY,  GRAY, GRAY],
    },
    
    'Bowtie': {
        'name': 'Motif L',
        'step': 2,
        'description': 'Forme L dans le coin',
        'U': [
            [GRAY,  WHITE, WHITE],
            [WHITE, WHITE, WHITE],
            [WHITE, WHITE, GRAY],
        ],
        'F': [GRAY,  GRAY, WHITE],
        'R': [GRAY,  GRAY, GRAY],
        'B': [GRAY,  GRAY, GRAY],
        'L': [WHITE, GRAY, GRAY],
    },
}


def get_two_look_oll_pattern(pattern_key):
    """
    Get 2-Look OLL pattern by key.
    """
    return TWO_LOOK_OLL_PATTERNS.get(pattern_key)


def get_step_patterns(step_number):
    """
    Get all patterns for a specific step.
    """
    return {
        key: pattern 
        for key, pattern in TWO_LOOK_OLL_PATTERNS.items() 
        if pattern['step'] == step_number
    }


def list_all_two_look_patterns():
    """Return list of all 2-Look OLL pattern keys"""
    return list(TWO_LOOK_OLL_PATTERNS.keys())