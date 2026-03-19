"""
Francontcube views module.

This module organizes views into a clean directory structure:
- base.py: Reusable utilities and base classes
- home.py: Home page and legacy views
- mosaic/: Pages for preparing mosaic  #NEW
- cubienewbie/: Apprenti Cubi method views (8 step views)
- beginner/: Beginner method views
- cfop/: CFOP method views
- roux/: Roux method views (coming soon)
- puzzles/: Other puzzles (2x2, 4x4, 5x5)

All views are exported from this module for easy URL routing.
"""

# ============================================================
# HOME & LEGACY VIEWS
# ============================================================
from .home import (
    home,
    mosaic,
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
# MOSAIC preparation # NEW
# ============================================================
from .mosaic.main import mosaic
from .mosaic.about import about as about
from .mosaic.mosaic_steps import mosaic_steps as mosaic_steps




# ============================================================
# CUBIE NEWBIE METHOD
# ============================================================
from .cubienewbie.main import method_cubienewbie
from .cubienewbie.daisy import daisy as cubienewbie_daisy
from .cubienewbie.bottom_cross import bottom_cross as cubienewbie_bottom_cross
from .cubienewbie.bottom_corners import bottom_corners as cubienewbie_bottom_corners
from .cubienewbie.second_layer import second_layer as cubienewbie_second_layer
from .cubienewbie.top_cross import top_cross as cubienewbie_top_cross
from .cubienewbie.top_face import top_face as cubienewbie_top_face
from .cubienewbie.corner_permutation import corner_permutation as cubienewbie_corner_permutation
from .cubienewbie.edge_permutation import edge_permutation as cubienewbie_edge_permutation
from .cubienewbie.cube_intro import cube_intro as cubienewbie_cube_intro
from .cubienewbie.notation import notation as cubienewbie_notation
from .cubienewbie.about import about as cubienewbie_about

# ============================================================
# BEGINNER METHOD
# ============================================================
from .beginner.main import method_beginner as beginner_method
from .beginner.bottom_cross import bottom_cross as beginner_bottom_cross
from .beginner.bottom_corners import bottom_corners as beginner_bottom_corners
from .beginner.second_layer import second_layer as beginner_second_layer
from .beginner.top_cross import top_cross as beginner_top_cross
from .beginner.top_face import top_face as beginner_top_face
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
# OTHER PUZZLES (2x2, 4x4, 5x5)
# ============================================================
from .puzzles.home import puzzles_home
from .puzzles.puzzle_2x2 import (
    puzzle_2x2_home,
    puzzle_2x2_method,
    puzzle_2x2_step,
)
from .puzzles.puzzle_big_cubes import (
    puzzle_4x4_home,
    puzzle_4x4_step,
    puzzle_5x5_home,
    puzzle_5x5_step,
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

    # Mosaic ****** NEW *******
    'mosaic',
    'about',
    'mosaic_steps',
    
    # Cubie Newbie
    'method_cubienewbie',
    'cubienewbie_about',
    'cubienewbie_cube_intro',
    'cubienewbie_notation',
    'cubienewbie_daisy',
    'cubienewbie_bottom_cross',
    'cubienewbie_bottom_corners',
    'cubienewbie_second_layer',
    'cubienewbie_top_cross',
    'cubienewbie_top_face',
    'cubienewbie_corner_permutation',
    'cubienewbie_edge_permutation',
    
    # Beginner Method
    'beginner_method',
    'beginner_about',
    'beginner_bottom_cross',
    'beginner_bottom_corners',
    'beginner_second_layer',
    'beginner_top_cross',
    'beginner_top_face',
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

    # Other puzzles
    'puzzles_home',
    'puzzle_2x2_home',
    'puzzle_2x2_method',
    'puzzle_2x2_step',
    'puzzle_4x4_home',
    'puzzle_4x4_step',
    'puzzle_5x5_home',
    'puzzle_5x5_step',
]