"""
Francontcube views module.

This module organizes views into a clean directory structure:
- base.py: Reusable utilities and base classes
- home.py: Home page and legacy views
- cubienewbie/: Apprenti Cubi method views (8 step views)
- cfop/: CFOP method views (coming soon)
- roux/: Roux method views (coming soon)

All views are exported from this module for easy URL routing.
"""

# ============================================================
# HOME & LEGACY VIEWS
# ============================================================
from .home import (
    home,
    method_beginner,
    method_f2l,
    method_roux,
    slides,
    pdfs,
    videos,
    ressources3par3,
    tutorial_step,
)

# ============================================================
# CUBIE NEWBIE METHOD
# ============================================================
from .cubienewbie.main import method_cubienewbie
from .cubienewbie.daisy import daisy as cubienewbie_daisy
from .cubienewbie.white_cross import white_cross as cubienewbie_white_cross
from .cubienewbie.bottom_corners import bottom_corners as cubienewbie_bottom_corners
from .cubienewbie.second_layer import second_layer as cubienewbie_second_layer
from .cubienewbie.yellow_cross import yellow_cross as cubienewbie_yellow_cross
from .cubienewbie.yellow_face import yellow_face as cubienewbie_yellow_face
from .cubienewbie.corner_permutation import corner_permutation as cubienewbie_corner_permutation
from .cubienewbie.edge_permutation import edge_permutation as cubienewbie_edge_permutation
from .cubienewbie.cube_intro import cube_intro as cubienewbie_cube_intro
from .cubienewbie.notation import notation as cubienewbie_notation
from .cubienewbie.about import about as cubienewbie_about

# ============================================================
# BEGINNER METHOD
# ============================================================
from .beginner.main import method_beginner as beginner_method
from .beginner.white_cross import white_cross as beginner_white_cross
from .beginner.bottom_corners import bottom_corners as beginner_bottom_corners
from .beginner.second_layer import second_layer as beginner_second_layer
from .beginner.yellow_cross import yellow_cross as beginner_yellow_cross
from .beginner.yellow_face import yellow_face as beginner_yellow_face
from .beginner.corner_permutation import corner_permutation as beginner_corner_permutation
from .beginner.edge_permutation import edge_permutation as beginner_edge_permutation
from .beginner.about import about as beginner_about

# ============================================================
# CFOP METHOD
# ============================================================
from .cfop.main import method_cfop
from .cfop.about import about as cfop_about
from .cfop.cross import cross as cfop_cross
from .cfop.f2l import cfop, cfop_f2l_basic  # ← Add this line
from .cfop.f2l import f2l as cfop_f2l
from .cfop.oll import oll as cfop_oll
from .cfop.pll import pll as cfop_pll




# ============================================================
# EXPORTS
# ============================================================
# List all views that should be accessible from francontcube.views
__all__ = [
    # Home & legacy
    'home',
    'method_beginner',
    'method_f2l',
    'method_roux',
    'slides',
    'pdfs',
    'videos',
    'ressources3par3',
    'tutorial_step',
    
    # Cubie Newbie (uncomment as migrated)
    'method_cubienewbie',
    'about',
    'cube_intro',
    'notation',
    'daisy',
    'white_cross',
    'bottom_corners',
    'second_layer',
    'yellow_cross',
    'yellow_face',
    'corner_permutation',
    'edge_permutation',

        # CFOP
    'method_cfop',
    'cfop_about',
    'cfop_cross',
    'cfop',                # ← Add this
    'cfop_f2l_basic',      # ← Add this
    'cfop_f2l',
    'cfop_oll',
    'cfop_pll',
]