# cube/two_look_pll_patterns.py
"""
2-Look PLL Pattern Definitions for SVG visualization.

Step 1: Corner Permutation (2 cases)
Step 2: Edge Permutation (4 cases)

These use simplified patterns for teaching purposes.
For PLL, the U face is always all yellow (everything oriented),
but the side colors show which pieces are swapped.
"""

# Color constants
YELLOW = '#FFD700'  # Top face (always yellow for PLL)
GREEN = '#00D800'   # Front face
RED = '#C41E3A'     # Right face
BLUE = '#0051BA'    # Back face
ORANGE = '#FF5800'  # Left face

# All yellow top face (used in all PLL cases)
ALL_YELLOW = [
    [YELLOW, YELLOW, YELLOW],
    [YELLOW, YELLOW, YELLOW],
    [YELLOW, YELLOW, YELLOW],
]

# ============================================================================
# 2-LOOK PLL PATTERNS
# ============================================================================

TWO_LOOK_PLL_PATTERNS = {
    # ========================================
    # STEP 1: Corner Permutation
    # ========================================
    
    'adjacent-corners': {
        'name': 'Adjacent Corners (Aa/Ab)',
        'step': 1,
        'description': 'Swap two adjacent corners - use Aa or Ab perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, ORANGE],   # One corner swapped
        'R': [RED, RED, RED],
        'B': [BLUE, BLUE, BLUE],
        'L': [GREEN, ORANGE, ORANGE],  # Swapped corner visible
    },
    
    'diagonal-corners': {
        'name': 'Diagonal Corners (Y/E)',
        'step': 1,
        'description': 'Swap two diagonal corners - use Y perm or E perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, ORANGE],   # Diagonal swap
        'R': [RED, RED, RED],
        'B': [GREEN, BLUE, BLUE],      # Diagonal swap
        'L': [ORANGE, ORANGE, ORANGE],
    },
    
    # ========================================
    # STEP 2: Edge Permutation (after corners are solved)
    # ========================================
    
    'three-edge-cycle': {
        'name': '3-Edge Cycle (Ua/Ub)',
        'step': 2,
        'description': 'Cycle 3 edges - use Ua or Ub perm',
        'U': ALL_YELLOW,
        'F': [GREEN, RED, GREEN],      # 3-cycle visible
        'R': [RED, BLUE, RED],
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, ORANGE, ORANGE], # One side solved
    },
    
    'opposite-edges': {
        'name': 'Opposite Edges (H)',
        'step': 2,
        'description': 'Swap opposite edge pairs - use H perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # Opposite swaps
        'R': [RED, ORANGE, RED],
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, RED, ORANGE],
    },
    
    'adjacent-edges': {
        'name': 'Adjacent Edges (Z)',
        'step': 2,
        'description': 'Swap adjacent edge pairs - use Z perm',
        'U': ALL_YELLOW,
        'F': [GREEN, RED, GREEN],      # Adjacent swaps
        'R': [RED, GREEN, RED],
        'B': [BLUE, ORANGE, BLUE],
        'L': [ORANGE, BLUE, ORANGE],
    },
    
    'solved': {
        'name': 'Solved',
        'step': 2,
        'description': 'All pieces in correct position - cube solved!',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],    # All correct
        'R': [RED, RED, RED],
        'B': [BLUE, BLUE, BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
}


def get_two_look_pll_pattern(pattern_key):
    """
    Get 2-Look PLL pattern by key.
    
    Args:
        pattern_key: Pattern identifier (e.g., 'adjacent-corners', 'three-edge-cycle')
    
    Returns:
        dict: Pattern dict with 'U', 'F', 'R', 'B', 'L' keys, or None if not found
    """
    return TWO_LOOK_PLL_PATTERNS.get(pattern_key)


def get_step_patterns(step_number):
    """
    Get all patterns for a specific step.
    
    Args:
        step_number: 1 for corners, 2 for edges
    
    Returns:
        dict: Dictionary of patterns for that step
    """
    return {
        key: pattern 
        for key, pattern in TWO_LOOK_PLL_PATTERNS.items() 
        if pattern['step'] == step_number
    }


def list_all_two_look_pll_patterns():
    """Return list of all 2-Look PLL pattern keys"""
    return list(TWO_LOOK_PLL_PATTERNS.keys())