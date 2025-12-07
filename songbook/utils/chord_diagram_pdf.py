"""
PDF-based chord diagram utilities.
Handles loading chord definitions, drawing diagrams on PDF canvas, and footer generation.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from django.conf import settings
from reportlab.platypus import Flowable
from reportlab.lib import colors
from reportlab.lib.units import inch

from .chord_diagram_svg import compute_base_fret, normalize_variation
from songbook.utils.transposer import clean_chord, transpose_chord

logger = logging.getLogger(__name__)


# Constants
STRING_SPACING = 15
FRET_SPACING = 15
DOT_RADIUS = 4
FRET_COUNT = 5


class ChordDiagram(Flowable):
    """
    Flowable class for embedding chord diagrams in ReportLab documents.
    """
    def __init__(
        self,
        chord_name: str,
        variation: Dict[str, Any],
        scale: float = 0.5,
        is_lefty: bool = False,
        instrument: str = "ukulele",
        variation_index: Optional[int] = None,
    ):
        super().__init__()
        self.chord_name = chord_name
        self.variation = normalize_variation(variation)
        self.scale = scale
        self.is_lefty = is_lefty
        self.instrument = instrument
        self.variation_index = variation_index

    def draw(self):
        """Draw the chord diagram on the canvas."""
        self.canv.saveState()
        self.canv.scale(self.scale, self.scale)

        # Add the variation index to the chord_name (e.g., "C[1]")
        display_name = self.chord_name
        if self.variation_index is not None:
            display_name = f"{display_name}[{self.variation_index}]"

        draw_chord_diagram(
            self.canv,
            0,
            0,
            self.variation,
            chord_name=display_name,
            instrument=self.instrument,
            is_lefty=self.is_lefty,
        )

        self.canv.restoreState()


def load_chords(instrument: str) -> List[Dict[str, Any]]:
    """
    Load chord definitions based on the selected instrument.
    Adds common aliases such as "Cmaj7" -> "CM7".
    
    Args:
        instrument: Instrument type (ukulele, guitar, etc.)
    
    Returns:
        List of chord definition dictionaries
    """
    chords_dir = os.path.join(settings.BASE_DIR, "songbook", "chords")
    file_map = {
        "ukulele": os.path.join(chords_dir, "ukulele.json"),
        "guitar": os.path.join(chords_dir, "guitar.json"),
        "guitalele": os.path.join(chords_dir, "guitalele.json"),
        "mandolin": os.path.join(chords_dir, "mandolin.json"),
        "banjo": os.path.join(chords_dir, "banjo.json"),
        "baritone_ukulele": os.path.join(chords_dir, "baritone_ukulele.json"),
    }

    file_path = file_map.get(instrument, file_map["ukulele"])
    logger.debug("Loading chords for instrument '%s' from %s", instrument, file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            chords = json.load(fh)
            logger.debug("Loaded %d chords for %s", len(chords), instrument)

            extended_chords: List[Dict[str, Any]] = []

            for chord in chords:
                chord_copy = dict(chord)
                chord_copy["instrument"] = instrument
                extended_chords.append(chord_copy)

                # Add alias: Cmaj7 -> CM7
                name = chord_copy.get("name", "")
                if name.endswith("maj7"):
                    alias = name.replace("maj7", "M7")
                    alias_chord = dict(chord_copy)
                    alias_chord["name"] = alias
                    extended_chords.append(alias_chord)

            added_aliases = len(extended_chords) - len(chords)
            logger.debug("Added %d alias chords for %s", added_aliases, instrument)
            return extended_chords

    except FileNotFoundError:
        logger.error("Chord file not found for %s at %s", instrument, file_path)
        return []
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format in %s: %s", file_path, e)
        return []


def extract_used_chords(lyrics_with_chords: Any) -> List[str]:
    """
    Extract chord names from a nested JSON-like structure.
    
    Args:
        lyrics_with_chords: Nested structure containing chord information
    
    Returns:
        Sorted list of unique chord names
    """
    chords = set()

    def traverse_structure(data: Any):
        if isinstance(data, dict):
            if "chord" in data and data["chord"]:
                chords.add(data["chord"])
            for value in data.values():
                traverse_structure(value)
        elif isinstance(data, list):
            for item in data:
                traverse_structure(item)

    traverse_structure(lyrics_with_chords)
    return sorted(chords)


def draw_footer(
    canvas,
    doc,
    relevant_chords: List[Dict[str, Any]],
    chord_spacing: int,
    row_spacing: int,
    is_lefty: bool,
    instrument: str = "ukulele",
    is_printing_alternate_chord: bool = False,
    acknowledgement: str = "",
):
    """
    Draw footer chord diagrams on the PDF.
    
    Args:
        canvas: ReportLab canvas object
        doc: Document object with pagesize info
        relevant_chords: List of chord definitions to display
        chord_spacing: Horizontal spacing between chords
        row_spacing: Vertical spacing between rows
        is_lefty: Mirror diagrams for left-handed players
        instrument: Instrument type
        is_printing_alternate_chord: Show alternate chord variations
        acknowledgement: Acknowledgement text to display
    """
    page_width, _ = doc.pagesize
    max_per_row = 12

    def prepare_chords(chords, is_printing_alternate_chord):
        """
        Prepare chord diagrams for rendering.
        Returns list of dicts with 'name' and 'variation'.
        """
        diagrams = []
        for chord in chords:
            display_name = chord.get("requested_name") or chord.get("name") or "?"
            raw = chord.get("variations") or chord.get("variation") or []

            # Normalize into a list
            if isinstance(raw, dict):
                variations = [raw]
            elif isinstance(raw, list):
                variations = raw
            else:
                variations = []

            # Get the selected variation index if stored
            selected_idx = chord.get("selected_variation_index", 0)

            # Draw the selected variation
            if selected_idx < len(variations):
                var_dict = normalize_variation(variations[selected_idx])
                var_dict["variation_index"] = selected_idx
                diagrams.append({
                    "name": display_name,
                    "variation": var_dict
                })

            # Draw alternate variation if enabled
            if is_printing_alternate_chord and len(variations) > 1:
                next_idx = (selected_idx + 1) % len(variations)
                var_dict = normalize_variation(variations[next_idx])
                var_dict["variation_index"] = next_idx
                diagrams.append({
                    "name": display_name,
                    "variation": var_dict
                })

        return diagrams

    primary_diagrams = prepare_chords(relevant_chords, is_printing_alternate_chord)

    # Calculate rows needed
    rows_needed = (len(primary_diagrams) + max_per_row - 1) // max_per_row if primary_diagrams else 0

    def draw_diagrams(diagrams: List[Dict[str, Any]], start_x: float, start_y: float, inst: str):
        """Draw a list of chord diagrams."""
        rows = [diagrams[i:i + max_per_row] for i in range(0, len(diagrams), max_per_row)]
        y_offset = start_y - (len(rows) - 1) * row_spacing if rows else start_y

        for row in rows:
            x_offset = start_x + (page_width / 2 - len(row) * chord_spacing / 2)

            for chord in row:
                display_name = clean_chord(chord.get("name", ""))
                diagram_var = chord.get("variation", {})
                variation_index = diagram_var.get("variation_index")

                diag = ChordDiagram(
                    display_name,
                    diagram_var,
                    scale=0.5,
                    is_lefty=is_lefty,
                    instrument=inst,
                    variation_index=variation_index,
                )
                diag.canv = canvas

                canvas.saveState()
                canvas.translate(x_offset, y_offset)
                diag.draw()
                canvas.restoreState()

                x_offset += chord_spacing

            y_offset -= row_spacing

        return start_y

    # Initial Y position
    start_y = 34 if rows_needed <= 1 else 172

    # Draw diagrams
    draw_diagrams(primary_diagrams, page_width / 4, start_y, instrument)

    # Acknowledgement line
    if acknowledgement:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawCentredString(
            doc.pagesize[0] / 2,
            0.2 * inch,
            f"Acknowledgement: {acknowledgement}"
        )


def draw_chord_diagram(
    c,
    x: float,
    y: float,
    variation: Any,
    chord_name: str = "",
    instrument: str = "ukulele",
    is_lefty: bool = False,
):
    """
    Draw a chord diagram directly on a PDF canvas.
    
    Args:
        c: ReportLab canvas object
        x: X position on canvas
        y: Y position on canvas
        variation: Chord variation (dict or list)
        chord_name: Display name of chord
        instrument: Instrument type
        is_lefty: Mirror for left-handed players
    """
    # Normalize variation
    if isinstance(variation, dict):
        positions = variation.get("positions", [])
        base_fret = variation.get("baseFret", compute_base_fret(positions))
        barre = variation.get("barre")
    else:
        positions = list(variation)
        base_fret = compute_base_fret(positions)
        barre = None

    # Mirror for lefties
    if is_lefty:
        positions = list(reversed(positions))
        if barre:
            string_count = len(positions)
            barre = {
                "fromString": (string_count + 1) - barre["toString"],
                "toString": (string_count + 1) - barre["fromString"],
                "fret": barre["fret"],
            }
        chord_name = clean_chord(chord_name)

    # Adjust frets relative to base-fret
    adjusted_positions = [
        (f - (base_fret - 1) if isinstance(f, int) and f > 0 else f)
        for f in positions
    ]

    string_count = max(1, len(positions))
    radius = DOT_RADIUS

    # Draw chord name with variation index if available
    if chord_name:
        label_name = chord_name
        if isinstance(variation, dict) and variation.get("variation_index") is not None:
            label_name += f"[{variation['variation_index']}]"

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(
            x + (string_count - 1) * STRING_SPACING / 2,
            y + FRET_COUNT * FRET_SPACING + 18,
            label_name
        )

    # Base fret label
    if base_fret > 1:
        label_x = x - 20 if not is_lefty else x + (string_count - 1) * STRING_SPACING + 5
        c.setFont("Helvetica", 14)
        c.drawString(label_x, y + FRET_COUNT * FRET_SPACING - 10, f"{base_fret}fr")

    # Draw strings
    for i in range(string_count):
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(
            x + i * STRING_SPACING,
            y,
            x + i * STRING_SPACING,
            y + FRET_COUNT * FRET_SPACING
        )

    # Draw frets
    for j in range(FRET_COUNT + 1):
        y_line = y + j * FRET_SPACING
        width = 4 if (j == FRET_COUNT and base_fret == 1) else 2
        c.setLineWidth(width)
        c.line(x, y_line, x + (string_count - 1) * STRING_SPACING, y_line)

    # Draw barre
    if barre:
        adj_fret = barre["fret"] - (base_fret - 1)
        if 1 <= adj_fret <= FRET_COUNT:
            start = barre["fromString"] - 1
            end = barre["toString"] - 1
            y_bar = y + (FRET_COUNT - adj_fret) * FRET_SPACING + FRET_SPACING / 2
            x_start = x + start * STRING_SPACING - radius
            width = (end - start) * STRING_SPACING + 2 * radius
            c.setFillColor(colors.black)
            c.roundRect(x_start, y_bar - radius, width, 2 * radius, 2, stroke=0, fill=1)

    # Draw fretted dots + muted/open strings
    for i, fret in enumerate(adjusted_positions):
        x_dot = x + i * STRING_SPACING

        if isinstance(fret, int) and fret > 0:
            y_dot = y + (FRET_COUNT - fret) * FRET_SPACING + FRET_SPACING / 2
            c.setFillColor(colors.black)
            c.circle(x_dot, y_dot, radius, stroke=0, fill=1)
        else:
            if instrument == "guitar":
                if fret == 0:
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(x_dot, y + FRET_COUNT * FRET_SPACING + 5, "O")
                elif fret == -1:
                    c.setFont("Helvetica", 11)
                    c.drawCentredString(x_dot, y + FRET_COUNT * FRET_SPACING + 4, "X")