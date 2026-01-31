"""
Francontcube views module.

This module organizes views into a clean directory structure:
- base.py: Reusable utilities and base classes
- home.py: Home page and legacy views
- cubienewbie/: Apprenti Cubi method views (8 step views)
- beginner/: Beginner method views
- cfop/: CFOP method views
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
from .cfop.f2l import cfop, cfop_f2l_basic

# CFOP Introduction Pages (NEW)
from .cfop.f2l_intro import cfop_f2l_intro
from .cfop.oll_intro import cfop_oll_intro
from .cfop.pll_intro import cfop_pll_intro

from .cfop.beginner_to_f2l import beginner_to_f2l_bridge



# 2-Look OLL
from .cfop.two_look_oll import two_look_oll_view

# OLL & PLL - New system with categories and filtering
from .cfop.oll_pll import (
    cfop_oll_view,
    cfop_pll_view,
    oll_case_detail,
    pll_case_detail,
)

# ============================================================
# EXPORTS
# ============================================================
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
    
    # Cubie Newbie
    'method_cubienewbie',
    'cubienewbie_about',
    'cubienewbie_cube_intro',
    'cubienewbie_notation',
    'cubienewbie_daisy',
    'cubienewbie_white_cross',
    'cubienewbie_bottom_corners',
    'cubienewbie_second_layer',
    'cubienewbie_yellow_cross',
    'cubienewbie_yellow_face',
    'cubienewbie_corner_permutation',
    'cubienewbie_edge_permutation',
    
    # Beginner Method
    'beginner_method',
    'beginner_about',
    'beginner_white_cross',
    'beginner_bottom_corners',
    'beginner_second_layer',
    'beginner_yellow_cross',
    'beginner_yellow_face',
    'beginner_corner_permutation',
    'beginner_edge_permutation',

    # CFOP
    'method_cfop',
    'cfop_about',
    'cfop_cross',
    'cfop',
    'cfop_f2l_basic',
    
    # CFOP Introduction Pages (NEW)
    'cfop_f2l_intro',
    'cfop_oll_intro',
    'cfop_pll_intro',
    'beginner_to_f2l_bridge',

    # OLL & PLL - New system
    'cfop_oll_view',
    'cfop_pll_view',
    'oll_case_detail',
    'pll_case_detail',
    'two_look_oll_view',
]