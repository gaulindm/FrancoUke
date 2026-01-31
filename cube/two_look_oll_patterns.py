# cube/two_look_oll_patterns.py
"""
2-Look OLL Pattern Definitions for SVG visualization.

Step 1: Cross patterns (3 cases)
Step 2: Corner patterns (7 cases)

These use simplified patterns for teaching purposes.
"""

# Color constants
YELLOW = '#FFD700'  # Oriented
GRAY = '#808080'    # Not oriented
GREEN = '#00D800'   # Front (default)
RED = '#C41E3A'     # Right (default)
BLUE = '#0051BA'    # Back (default)
ORANGE = '#FF5800'  # Left (default)

# ============================================================================
# 2-LOOK OLL PATTERNS
# ============================================================================

TWO_LOOK_OLL_PATTERNS = {
    # ========================================
    # STEP 1: Yellow Cross (Edge Orientation)
    # ========================================
    
    'dot-cross': {
        'name': 'Dot → Cross',
        'step': 1,
        'description': 'No edges oriented - make a yellow cross',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ],
        'F': [GRAY, YELLOW, GRAY],
        'R': [GRAY, YELLOW, GRAY],
        'B': [GRAY, YELLOW, GRAY],
        'L': [GRAY, YELLOW, GRAY],
    },
    
    'line-cross': {
        'name': 'Line → Cross',
        'step': 1,
        'description': 'Horizontal line of 2 edges',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ],
        'F': [GRAY, YELLOW, GRAY],
        'R': [GRAY, GRAY, GRAY],
        'B': [GRAY, YELLOW, GRAY],
        'L': [GRAY, GRAY, GRAY],
    },
    
    'l-cross': {
        'name': 'L-Shape → Cross',
        'step': 1,
        'description': 'L-shape of 2 edges on left',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ],
        'F': [GRAY, GRAY, GRAY],
        'R': [GRAY, GRAY, GRAY],
        'B': [GRAY, YELLOW, GRAY],
        'L': [GRAY, YELLOW, GRAY],
    },
    
    # ========================================
    # STEP 2: Yellow Face (Corner Orientation)
    # After cross is done, U face edges are all yellow
    # ========================================
    
    'sune': {
        'name': 'Sune',
        'step': 2,
        'description': 'Fish pattern - headlights on right',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
        ],
        'F': [GRAY, GRAY, YELLOW],
        'R': [YELLOW, GRAY, GRAY ],
        'B': [YELLOW, GRAY, GRAY],
        'L': [GRAY, GRAY, GRAY],
    },
    
    'antisune': {
        'name': 'Anti-Sune',
        'step': 2,
        'description': 'Fish pattern - headlights on left',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
        ],
        'F': [YELLOW, GRAY, GRAY],
        'R': [GRAY, GRAY, GRAY],
        'B': [GRAY, GRAY, YELLOW],
        'L': [YELLOW, GRAY, GRAY],
    },
    
    'h-pattern': {
        'name': 'H Pattern',
        'step': 2,
        'description': 'Checkerboard pattern - 2 opposite corners',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ],
        'F': [GRAY, GRAY, GRAY],
        'R': [YELLOW, GRAY, YELLOW],
        'B': [GRAY, GRAY, GRAY],
        'L': [YELLOW, GRAY, YELLOW],
    },
    
    'pi-pattern': {
        'name': 'Pi Pattern',
        'step': 2,
        'description': 'Two headlights in front',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY]
        ],
        'F': [GRAY, GRAY, YELLOW],
        'R': [GRAY, GRAY, GRAY],
        'B': [GRAY, GRAY, YELLOW],
        'L': [YELLOW, GRAY, YELLOW],
    },
    
    'u-pattern': {
        'name': 'U Pattern',
        'step': 2,
        'description': 'U-shape facing front',
        'U': [
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ],
        'F': [YELLOW, GRAY, YELLOW],
        'R': [GRAY, GRAY, GRAY],
        'B': [GRAY, GRAY, GRAY],
        'L': [GRAY, GRAY, GRAY],
    },
    
    't-pattern': {
        'name': 'T Pattern',
        'step': 2,
        'description': 'T-shape at front',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
        ],
        'F': [YELLOW, GRAY, GRAY],
        'R': [GRAY, GRAY, GRAY],
        'B': [YELLOW, GRAY, GRAY],
        'L': [GRAY, GRAY, GRAY],
    },
    
    'Bowtie': {
        'name': 'Bowtie',
        'step': 2,
        'description': 'L-shape in corner',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
        ],
        'F': [GRAY, GRAY, YELLOW],
        'R': [GRAY, GRAY, GRAY],
        'B': [GRAY, GRAY, GRAY],
        'L': [YELLOW, GRAY, GRAY],
    },
}


def get_two_look_oll_pattern(pattern_key):
    """
    Get 2-Look OLL pattern by key.
    
    Args:
        pattern_key: Pattern identifier (e.g., 'dot-cross', 'sune')
    
    Returns:
        dict: Pattern dict with 'U', 'F', 'R', 'B', 'L' keys, or None if not found
    """
    return TWO_LOOK_OLL_PATTERNS.get(pattern_key)


def get_step_patterns(step_number):
    """
    Get all patterns for a specific step.
    
    Args:
        step_number: 1 for cross, 2 for corners
    
    Returns:
        dict: Dictionary of patterns for that step
    """
    return {
        key: pattern 
        for key, pattern in TWO_LOOK_OLL_PATTERNS.items() 
        if pattern['step'] == step_number
    }


def list_all_two_look_patterns():
    """Return list of all 2-Look OLL pattern keys"""
    return list(TWO_LOOK_OLL_PATTERNS.keys())