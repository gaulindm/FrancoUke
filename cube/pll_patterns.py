# cube/pll_patterns.py
"""
PLL (Permutation of Last Layer) top layer patterns for SVG visualization.

All 21 PLL cases showing edge and corner permutations.
For PLL, the U face is all yellow (everything is oriented), but the side colors
show which pieces are swapped.

Pattern format:
{
    'slug': {
        'U': [[YELLOW] * 3] * 3,  # Always all yellow for PLL
        'F': [color_left, color_middle, color_right],  # Front face top row
        'R': [color_left, color_middle, color_right],  # Right face top row
        'B': [color_left, color_middle, color_right],  # Back face top row
        'L': [color_left, color_middle, color_right],  # Left face top row
    }
}
"""

# Color constants
YELLOW = '#FFD700'  # Top face (always yellow for PLL)
GREEN = '#00D800'   # Front face
RED = '#C41E3A'     # Right face
BLUE = '#0051BA'    # Back face
ORANGE = '#FF5800'  # Left face

# Helper for solved U face (always all yellow in PLL)
ALL_YELLOW = [
    [YELLOW, YELLOW, YELLOW],
    [YELLOW, YELLOW, YELLOW],
    [YELLOW, YELLOW, YELLOW],
]

# ============================================================================
# PLL PATTERNS - Organized by category
# ============================================================================

PLL_PATTERNS = {
    # ========================================
    # Solved (1 case)
    # ========================================
    'pll-solved': {
        'name': 'PLL - Solved',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [RED, RED, RED],
        'B': [BLUE, BLUE, BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    
    # ========================================
    # Edges Only - Ua, Ub, H, Z (4 cases)
    # ========================================
    'pll-ua': {
        'name': 'PLL - Ua Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, RED, GREEN],      # 3-cycle: F→R→B→F
        'R': [RED, BLUE, RED],
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, ORANGE, ORANGE], # L unchanged
    },
    'pll-ub': {
        'name': 'PLL - Ub Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # 3-cycle reverse: F→B→R→F
        'R': [RED, GREEN, RED],
        'B': [BLUE, RED, BLUE],
        'L': [ORANGE, ORANGE, ORANGE], # L unchanged
    },
    'pll-h': {
        'name': 'PLL - H Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # Opposite pairs swapped
        'R': [RED, ORANGE, RED],       # F↔B, R↔L
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, RED, ORANGE],
    },
    'pll-z': {
        'name': 'PLL - Z Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, RED, GREEN],      # Adjacent pairs swapped
        'R': [RED, GREEN, RED],        # F↔R, B↔L
        'B': [BLUE, ORANGE, BLUE],
        'L': [ORANGE, BLUE, ORANGE],
    },
    
    # ========================================
    # Adjacent Corner Swap - Aa, Ab, E (3 cases)
    # ========================================
    'pll-aa': {
        'name': 'PLL - Aa Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [RED, BLUE, RED],         # Corners rotated clockwise
        'B': [BLUE, BLUE, ORANGE],     # + edge cycle
        'L': [ORANGE, ORANGE, RED],
    },
    'pll-ab': {
        'name': 'PLL - Ab Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [ORANGE, BLUE, RED],      # Corners rotated counter-clockwise
        'B': [RED, BLUE, BLUE],        # + edge cycle
        'L': [ORANGE, ORANGE, ORANGE],
    },
    'pll-e': {
        'name': 'PLL - E Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # All edges swapped in pairs
        'R': [RED, ORANGE, RED],
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, RED, ORANGE],
    },
    
    # ========================================
    # Adjacent Swap - T, J, R, F (8 cases)
    # ========================================
    'pll-t': {
        'name': 'PLL - T Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # Two adjacent edges swap
        'R': [RED, RED, RED],
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    'pll-ja': {
        'name': 'PLL - Ja Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [RED, BLUE, ORANGE],      # Adjacent corner + edge swap
        'B': [BLUE, RED, BLUE],
        'L': [ORANGE, ORANGE, RED],
    },
    'pll-jb': {
        'name': 'PLL - Jb Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [ORANGE, BLUE, RED],      # Mirror of Ja
        'B': [BLUE, RED, BLUE],
        'L': [RED, ORANGE, ORANGE],
    },
    'pll-ra': {
        'name': 'PLL - Ra Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, ORANGE],   # Adjacent corner swap
        'R': [RED, BLUE, RED],         # + edge cycle
        'B': [BLUE, BLUE, BLUE],
        'L': [ORANGE, ORANGE, GREEN],
    },
    'pll-rb': {
        'name': 'PLL - Rb Perm',
        'U': ALL_YELLOW,
        'F': [ORANGE, GREEN, GREEN],   # Mirror of Ra
        'R': [RED, BLUE, RED],
        'B': [BLUE, BLUE, BLUE],
        'L': [GREEN, ORANGE, ORANGE],
    },
    'pll-f': {
        'name': 'PLL - F Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [ORANGE, BLUE, RED],      # Complex adjacent swap
        'B': [RED, BLUE, BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    'pll-ga': {
        'name': 'PLL - Ga Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, ORANGE],   # G-perm family
        'R': [RED, BLUE, RED],
        'B': [BLUE, BLUE, GREEN],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    'pll-gb': {
        'name': 'PLL - Gb Perm',
        'U': ALL_YELLOW,
        'F': [ORANGE, GREEN, GREEN],   # G-perm variation
        'R': [RED, BLUE, RED],
        'B': [GREEN, BLUE, BLUE],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    'pll-gc': {
        'name': 'PLL - Gc Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],    # G-perm variation
        'R': [RED, BLUE, ORANGE],
        'B': [BLUE, BLUE, BLUE],
        'L': [GREEN, ORANGE, ORANGE],
    },
    'pll-gd': {
        'name': 'PLL - Gd Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],    # G-perm variation
        'R': [ORANGE, BLUE, RED],
        'B': [BLUE, BLUE, BLUE],
        'L': [ORANGE, ORANGE, GREEN],
    },
    
    # ========================================
    # Diagonal Corner Swap - Y, V, Na, Nb (4 cases)
    # ========================================
    'pll-y': {
        'name': 'PLL - Y Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, GREEN],
        'R': [ORANGE, RED, RED],       # Diagonal corners
        'B': [BLUE, BLUE, BLUE],       # + edges
        'L': [ORANGE, ORANGE, RED],
    },
    'pll-v': {
        'name': 'PLL - V Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, GREEN, ORANGE],   # Diagonal swap
        'R': [RED, RED, RED],
        'B': [BLUE, BLUE, GREEN],
        'L': [ORANGE, ORANGE, ORANGE],
    },
    'pll-na': {
        'name': 'PLL - Na Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # N-perm: diagonal + edges
        'R': [ORANGE, RED, RED],
        'B': [BLUE, GREEN, BLUE],
        'L': [RED, ORANGE, ORANGE],
    },
    'pll-nb': {
        'name': 'PLL - Nb Perm',
        'U': ALL_YELLOW,
        'F': [GREEN, BLUE, GREEN],     # Mirror of Na
        'R': [RED, RED, ORANGE],
        'B': [BLUE, GREEN, BLUE],
        'L': [ORANGE, ORANGE, RED],
    },
}


def get_pll_pattern(slug):
    """
    Get PLL pattern by slug.
    
    Args:
        slug: Case slug (e.g., 'pll-t')
    
    Returns:
        dict: Pattern dict with 'U', 'F', 'R', 'B', 'L' keys, or None if not found
    """
    return PLL_PATTERNS.get(slug)


def list_all_pll_cases():
    """Return list of all PLL case slugs"""
    return list(PLL_PATTERNS.keys())