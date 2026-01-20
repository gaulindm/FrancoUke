# cube/oll_patterns.py
"""
OLL (Orientation of Last Layer) top layer patterns for SVG visualization.

All 57 OLL cases showing which pieces are oriented (yellow) vs not oriented (gray).
The U face shows the orientation pattern, while side faces show default colors.

Pattern format:
{
    'slug': {
        'U': [
            [row0_col0, row0_col1, row0_col2],
            [row1_col0, row1_col1, row1_col2],
            [row2_col0, row2_col1, row2_col2],
        ]
    }
}
"""

# Color constants
YELLOW = '#FFD700'  # Oriented piece
GRAY = '#808080'    # Not oriented piece
GREEN = '#00D800'   # Front face (default)
RED = '#C41E3A'     # Right face (default)
BLUE = '#0051BA'    # Back face (default)
ORANGE = '#FF5800'  # Left face (default)

# Helper for all yellow (fully oriented)
ALL_YELLOW = [[YELLOW, YELLOW, YELLOW]] * 3

# Helper for all gray except center (dot pattern base)
DOT = [
    [GRAY, GRAY, GRAY],
    [GRAY, YELLOW, GRAY],
    [GRAY, GRAY, GRAY],
]

# ============================================================================
# OLL PATTERNS - Organized by shape
# ============================================================================

OLL_PATTERNS = {
    # ========================================
    # All Edges Oriented Correctly (1 case)
    # ========================================
    'oll-01': {
        'name': 'OLL #1 - Already Oriented',
        'U': [
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    
    # ========================================
    # Dot Cases - No edges oriented (8 cases)
    # ========================================
    'oll-02': {
        'name': 'OLL #2 - Sune',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-03': {
        'name': 'OLL #3 - Anti-Sune',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-04': {
        'name': 'OLL #4 - Dot',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-17': {
        'name': 'OLL #17 - Dot',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-18': {
        'name': 'OLL #18 - Dot',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-19': {
        'name': 'OLL #19 - Dot',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-20': {
        'name': 'OLL #20 - Dot',
        'U': [
            [GRAY, GRAY, GRAY],
            [GRAY, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    
    # ========================================
    # Line Cases - 2 opposite edges (8 cases)
    # ========================================
    'oll-51': {
        'name': 'OLL #51 - Line',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-52': {
        'name': 'OLL #52 - Line',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-55': {
        'name': 'OLL #55 - Line',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-56': {
        'name': 'OLL #56 - Line',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-53': {
        'name': 'OLL #53 - Line',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-54': {
        'name': 'OLL #54 - Line',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    
    # ========================================
    # Square Cases (4 cases)
    # ========================================
    'oll-05': {
        'name': 'OLL #5 - Square',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, GRAY],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-06': {
        'name': 'OLL #6 - Square',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    
    # ========================================
    # Small Lightning Cases (4 cases)
    # ========================================
    'oll-07': {
        'name': 'OLL #7 - Small Lightning',
        'U': [
            [YELLOW, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-08': {
        'name': 'OLL #8 - Small Lightning',
        'U': [
            [GRAY, GRAY, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-11': {
        'name': 'OLL #11 - Small Lightning',
        'U': [
            [YELLOW, GRAY, GRAY],
            [YELLOW, YELLOW, GRAY],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-12': {
        'name': 'OLL #12 - Small Lightning',
        'U': [
            [GRAY, GRAY, YELLOW],
            [GRAY, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    
    # ========================================
    # Fish Cases (4 cases)
    # ========================================
    'oll-09': {
        'name': 'OLL #9 - Fish',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-10': {
        'name': 'OLL #10 - Fish',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, GRAY],
        ]
    },
    'oll-35': {
        'name': 'OLL #35 - Fish',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, GRAY, YELLOW],
        ]
    },
    'oll-37': {
        'name': 'OLL #37 - Fish',
        'U': [
            [GRAY, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, GRAY, YELLOW],
        ]
    },
    
    # ========================================
    # L-Shape Cases (6 cases)
    # ========================================
    'oll-47': {
        'name': 'OLL #47 - L-Shape',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, GRAY],
            [YELLOW, GRAY, GRAY],
        ]
    },
    'oll-48': {
        'name': 'OLL #48 - L-Shape',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
            [GRAY, GRAY, YELLOW],
        ]
    },
    'oll-49': {
        'name': 'OLL #49 - L-Shape',
        'U': [
            [GRAY, GRAY, YELLOW],
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    'oll-50': {
        'name': 'OLL #50 - L-Shape',
        'U': [
            [YELLOW, GRAY, GRAY],
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    
    # ========================================
    # Knight Move Cases (8 cases)
    # ========================================
    'oll-13': {
        'name': 'OLL #13 - Knight',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, GRAY, GRAY],
        ]
    },
    'oll-14': {
        'name': 'OLL #14 - Knight',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, YELLOW],
        ]
    },
    'oll-15': {
        'name': 'OLL #15 - Knight',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
            [GRAY, GRAY, YELLOW],
        ]
    },
    'oll-16': {
        'name': 'OLL #16 - Knight',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [GRAY, YELLOW, YELLOW],
            [YELLOW, GRAY, GRAY],
        ]
    },
    
    # ========================================
    # P-Shape Cases (4 cases)
    # ========================================
    'oll-31': {
        'name': 'OLL #31 - P-Shape',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
        ]
    },
    'oll-32': {
        'name': 'OLL #32 - P-Shape',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
        ]
    },
    'oll-43': {
        'name': 'OLL #43 - P-Shape',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-44': {
        'name': 'OLL #44 - P-Shape',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    
    # ========================================
    # W-Shape Cases (2 cases)
    # ========================================
    'oll-36': {
        'name': 'OLL #36 - W-Shape',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, GRAY, YELLOW],
        ]
    },
    'oll-38': {
        'name': 'OLL #38 - W-Shape',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, GRAY, YELLOW],
        ]
    },
    
    # ========================================
    # T-Shape Cases (2 cases)
    # ========================================
    'oll-33': {
        'name': 'OLL #33 - T-Shape',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    'oll-45': {
        'name': 'OLL #45 - T-Shape',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    
    # ========================================
    # C-Shape Cases (2 cases)
    # ========================================
    'oll-34': {
        'name': 'OLL #34 - C-Shape',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
        ]
    },
    'oll-46': {
        'name': 'OLL #46 - C-Shape',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
        ]
    },
    
    # ========================================
    # Awkward Cases (4 cases)
    # ========================================
    'oll-29': {
        'name': 'OLL #29 - Awkward',
        'U': [
            [YELLOW, GRAY, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    'oll-30': {
        'name': 'OLL #30 - Awkward',
        'U': [
            [GRAY, GRAY, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
        ]
    },
    'oll-41': {
        'name': 'OLL #41 - Awkward',
        'U': [
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, GRAY, GRAY],
        ]
    },
    'oll-42': {
        'name': 'OLL #42 - Awkward',
        'U': [
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, GRAY, YELLOW],
        ]
    },
    
    # ========================================
    # I-Shape Cases (4 cases)
    # ========================================
    'oll-39': {
        'name': 'OLL #39 - I-Shape',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
        ]
    },
    'oll-40': {
        'name': 'OLL #40 - I-Shape',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
        ]
    },
    
    # ========================================
    # Big Lightning Cases (4 cases)
    # ========================================
    'oll-25': {
        'name': 'OLL #25 - Big Lightning',
        'U': [
            [GRAY, YELLOW, YELLOW],
            [YELLOW, YELLOW, GRAY],
            [YELLOW, YELLOW, GRAY],
        ]
    },
    'oll-27': {
        'name': 'OLL #27 - Big Lightning',
        'U': [
            [YELLOW, YELLOW, GRAY],
            [GRAY, YELLOW, YELLOW],
            [GRAY, YELLOW, YELLOW],
        ]
    },
    
    # ========================================
    # Cross Cases - All edges oriented (7 cases)
    # ========================================
    'oll-21': {
        'name': 'OLL #21 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-22': {
        'name': 'OLL #22 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-23': {
        'name': 'OLL #23 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-24': {
        'name': 'OLL #24 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-26': {
        'name': 'OLL #26 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-28': {
        'name': 'OLL #28 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
    'oll-57': {
        'name': 'OLL #57 - Cross',
        'U': [
            [GRAY, YELLOW, GRAY],
            [YELLOW, YELLOW, YELLOW],
            [GRAY, YELLOW, GRAY],
        ]
    },
}


def get_oll_pattern(slug):
    """
    Get OLL pattern by slug.
    
    Args:
        slug: Case slug (e.g., 'oll-02')
    
    Returns:
        dict: Pattern dict with 'U' key, or None if not found
    """
    return OLL_PATTERNS.get(slug)


def list_all_oll_cases():
    """Return list of all OLL case slugs"""
    return list(OLL_PATTERNS.keys())