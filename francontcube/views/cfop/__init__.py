"""
CFOP method views.

CFOP (Cross, F2L, OLL, PLL) is the most popular speedcubing method.
"""

from .main import method_cfop
from .about import about
from .cross import cross
from .f2l import f2l
from .oll import oll
from .pll import pll

__all__ = [
    'method_cfop',
    'about',
    'cross',
    'f2l',
    'oll',
    'pll',
]