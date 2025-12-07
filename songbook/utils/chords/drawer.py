from typing import List, Dict, Any, Optional
from reportlab.lib.units import inch
from reportlab.platypus import Flowable
from reportlab.lib import colors
#from songbook.utils.chord_utils import ChordDiagram, normalize_variation, clean_chord
from songbook.utils.chords.diagrams import ChordDiagram
from songbook.utils.transposer import clean_chord
from songbook.utils.chords.variation_rules import parse_requested_variation
from songbook.utils.chords.normalize import normalize_variation

from typing import List, Dict, Any, Optional
#from songbook.utils.chords.diagrams import prepare_chords, draw_diagrams, MAX_CHORDS_PER_ROW


MAX_CHORDS_PER_ROW = 14


def prepare_chords(chords: List[Dict[str, Any]], is_printing_alternate_chord: bool):
    """
    Prepare chord diagrams from the variations already selected in load_relevant_chords.
    Simply iterate through all variations and create a diagram for each.
    """

    diagrams = []

    for chord in chords:
        chord_name = chord.get("name") or "?"
        raw = chord.get("variations") or chord.get("variation") or []

        # Normalize to list
        if isinstance(raw, dict):
            variations = [raw]
        else:
            variations = raw

        if not variations:
            continue

        # Add ALL variations that were selected by load_relevant_chords
        for idx, var in enumerate(variations):
            normalized_var = normalize_variation(var)
            diagrams.append({
                "name": chord_name,
                "variation": normalized_var,
                "variation_index": idx,
            })

    print("[DEBUG] Prepared diagrams count =", len(diagrams))
    for d in diagrams:
        print("   ->", d["name"], "v", d["variation_index"], d["variation"])

    return diagrams


def draw_diagrams(
    canvas,
    diagrams: List[Dict[str, Any]],
    start_x: float,
    start_y: float,
    chord_spacing: int,
    row_spacing: int,
    is_lefty: bool,
    instrument: str,
):
    """
    Draw chord diagrams on canvas in rows, centered horizontally.
    """
    rows = [diagrams[i:i + MAX_CHORDS_PER_ROW] for i in range(0, len(diagrams), MAX_CHORDS_PER_ROW)]
    y_offset = start_y - (len(rows) - 1) * row_spacing if rows else start_y

    for row in rows:
        x_offset = start_x + (canvas._pagesize[0] / 2 - len(row) * chord_spacing / 2)
        for chord in row:
            display_name = clean_chord(chord.get("name", ""))
            diagram_var = chord.get("variation", {})
            diag = ChordDiagram(display_name, diagram_var, scale=0.5, is_lefty=is_lefty, instrument=instrument)
            diag.canv = canvas

            canvas.saveState()
            canvas.translate(x_offset, y_offset)

            diag.draw()
            canvas.restoreState()

            x_offset += chord_spacing
        y_offset -= row_spacing



def draw_footer(
    canvas,
    doc,
    relevant_chords: list,
    chord_spacing: int = 50,
    row_spacing: int = 70,
    is_lefty: bool = False,
    instrument: str = "ukulele",
    secondary_instrument: Optional[str] = None,
    is_printing_alternate_chord: bool = False,
    acknowledgement: str = "",
):
    """
    Draw footer chord diagrams, dynamically adjusting number per row and vertical position.
    """

    primary_chords = [ch for ch in relevant_chords if ch.get("instrument") == instrument]
    primary_diagrams = prepare_chords(primary_chords, is_printing_alternate_chord)

    if not primary_diagrams:
        return

    page_width, page_height = canvas._pagesize
    ack_height = 20
    bottom_margin = 10 + ack_height

    # -------------------------
    # Determine max chords per row dynamically
    # -------------------------
    max_possible_per_row = len(primary_diagrams)
    while (max_possible_per_row - 1) * chord_spacing > page_width * 0.9 and max_possible_per_row > 1:
        max_possible_per_row -= 1

    MAX_CHORDS_PER_ROW = max_possible_per_row

    # -------------------------
    # Rows and scaling
    # -------------------------
    rows = [primary_diagrams[i:i + MAX_CHORDS_PER_ROW] for i in range(0, len(primary_diagrams), MAX_CHORDS_PER_ROW)]
    rows_needed = len(rows)

    # Define a safe margin above the bottom (for acknowledgement)
    ack_height = 20  # height reserved for acknowledgement line
    bottom_margin_safe = bottom_margin + ack_height

    # Compute total height occupied by rows
    total_rows_height = rows_needed * row_spacing

    # Start drawing the top row just above bottom safe margin
    start_y = bottom_margin_safe + total_rows_height - row_spacing  - 10 # top of first row


    # -------------------------
    # Draw diagrams
    # -------------------------
    y_offset = start_y
    for row in rows:
        row_width = (len(row) - 1) * chord_spacing
        x_offset = (page_width - row_width) / 2  # center row

        for chord in row:
            display_name = clean_chord(chord.get("name", ""))
            diagram_var = chord.get("variation", {})

            diag = ChordDiagram(
                display_name,
                diagram_var,
                scale=0.5,  # base scale, adjust if needed
                is_lefty=is_lefty,
                instrument=instrument
            )
            diag.canv = canvas

            canvas.saveState()
            canvas.translate(x_offset, y_offset)
            diag.draw()
            canvas.restoreState()

            x_offset += chord_spacing

        y_offset -= row_spacing

    # -------------------------
    # Draw acknowledgement
    # -------------------------
    if acknowledgement:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(page_width / 2, bottom_margin - ack_height / 2, f"Acknowledgement: {acknowledgement}")
