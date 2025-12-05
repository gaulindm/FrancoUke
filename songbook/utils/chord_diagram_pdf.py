"""
chord_diagram_pdf.py
--------------------------------
This module provides a clean, minimal interface for drawing footer chord
diagrams inside PDF documents.

All chord selection, normalization, and diagram rendering logic now lives in:

    songbook.utils.chords.drawer

This module simply delegates to drawer.draw_footer().
"""

from typing import List, Dict, Any, Optional
from reportlab.lib.units import inch

# Canonical chord rendering module
from songbook.utils.chords.drawer import draw_footer as drawer_draw_footer


def draw_footer(
    canvas,
    doc,
    relevant_chords: List[Dict[str, Any]],
    chord_spacing: int = 50,
    row_spacing: int = 70,
    is_lefty: bool = False,
    instrument: str = "ukulele",
    secondary_instrument: Optional[str] = None,
    is_printing_alternate_chord: bool = False,
    acknowledgement: str = "",
):
    """
    Thin wrapper around drawer.draw_footer().
    
    All chord logic — selecting, normalizing, and rendering chord diagrams —
    happens in drawer.py.

    This function exists for backward compatibility with PDF layout code that 
    imports draw_footer from this module.
    """

    return drawer_draw_footer(
        canvas=canvas,
        doc=doc,
        relevant_chords=relevant_chords,
        chord_spacing=chord_spacing,
        row_spacing=row_spacing,
        is_lefty=is_lefty,
        instrument=instrument,
        secondary_instrument=secondary_instrument,
        is_printing_alternate_chord=is_printing_alternate_chord,
        acknowledgement=acknowledgement,
    )
