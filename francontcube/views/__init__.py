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
# NOTE: Uncomment these as you migrate each view to the new structure
from .cubienewbie.main import method_cubienewbie
from .cubienewbie.daisy import daisy
from .cubienewbie.white_cross import white_cross
from .cubienewbie.bottom_corners import bottom_corners
from .cubienewbie.second_layer import second_layer
from .cubienewbie.yellow_cross import yellow_cross
from .cubienewbie.yellow_face import yellow_face
from .cubienewbie.corner_permutation import corner_permutation
from .cubienewbie.edge_permutation import edge_permutation

# ============================================================
# OTHER METHODS
# ============================================================
# Add imports here as you implement other methods:
# from .cfop.main import method_cfop
# from .cfop.cross import cfop_cross
# from .cfop.f2l import cfop_f2l
# from .cfop.oll import cfop_oll
# from .cfop.pll import cfop_pll

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
    'daisy',
    'white_cross',
    'bottom_corners',
    'second_layer',
    'yellow_cross',
    'yellow_face',
    'corner_permutation',
    'edge_permutation',
    
    # Other methods (add as implemented)
    # 'method_cfop',
    # 'cfop_cross',
    # 'cfop_f2l',
    # 'cfop_oll',
    # 'cfop_pll',
]