from typing import List, Dict, Any, Optional
from reportlab.lib.units import inch
from reportlab.platypus import Flowable
from reportlab.lib import colors
#from songbook.utils.chord_utils import ChordDiagram, normalize_variation, clean_chord
from songbook.utils.chords.diagrams import ChordDiagram
from songbook.utils.transposer import clean_chord
from songbook.utils.chords.variation_rules import parse_requested_variation, select_variations
from songbook.utils.chords.normalize import normalize_variation


MAX_CHORDS_PER_ROW = 14


def prepare_chords(chords: List[Dict[str, Any]], is_printing_alternate_chord: bool):
    """
    Goal:
    ALWAYS show:
        - variation 0
        - variation 1 (if exists)

    If the song requests a specific variation (e.g. [C(2)]),
    then use that instead for the FIRST slot but still show
    variation 1 as the alternate.
    """

    diagrams = []

    for chord in chords:
        requested_name = chord.get("requested_name") or chord.get("name") or "?"
        base, forced_index = parse_requested_variation(requested_name)

        raw = chord.get("variations") or chord.get("variation") or []

        # Normalize to list
        if isinstance(raw, dict):
            variations = [raw]
        else:
            variations = raw

        if not variations:
            continue

        # --- 1) SELECTED (PRIMARY) VARIATION ---
        if forced_index is not None and forced_index < len(variations):
            main_idx = forced_index
        else:
            main_idx = 0  # default

        main_var = normalize_variation(variations[main_idx])
        diagrams.append({
            "name": base,
            "variation": main_var,
            "variation_index": main_idx,
        })

        # --- 2) ALTERNATE (SECOND) VARIATION ---
        if len(variations) > 1:
            alt_idx = 1  # always use variation 1 as alternate
            alt_var = normalize_variation(variations[alt_idx])

            diagrams.append({
                "name": base,
                "variation": alt_var,
                "variation_index": alt_idx,
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

            # --- DEBUG RECTANGLE ---
            canvas.setStrokeColor(colors.red)
            canvas.setLineWidth(1)
            rect_width = 60  # approx width of diagram
            rect_height = 80  # approx height of diagram
            canvas.rect(0, 0, rect_width, rect_height, stroke=1, fill=0)
            print(f"[DEBUG] Drawing debug rect at X={x_offset}, Y={y_offset}")

            diag.draw()
            canvas.restoreState()

            x_offset += chord_spacing
        y_offset -= row_spacing


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
    Draw footer chord diagrams for primary instrument only.
    """
    print("\n" + "="*80)
    print("DRAW_FOOTER CALLED")
    print("is_printing_alternate_chord =", is_printing_alternate_chord)
    print("instrument =", instrument)
    print("TOTAL relevant chords =", len(relevant_chords))
    print("="*80 + "\n")




    primary_chords = [ch for ch in relevant_chords if ch.get("instrument") == instrument]
    primary_diagrams = prepare_chords(primary_chords, is_printing_alternate_chord)

    # DEBUG OUTPUT
    print("Prepared diagrams count =", len(primary_diagrams))
    for d in primary_diagrams:
        print("   ->", d.get("name"), d.get("variation"))

    rows_needed = (len(primary_diagrams) + MAX_CHORDS_PER_ROW - 1) // MAX_CHORDS_PER_ROW
    start_y = 172 if rows_needed > 1 else 150


    draw_diagrams(canvas, primary_diagrams, 0, start_y, chord_spacing, row_spacing, is_lefty, instrument)



    if acknowledgement:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.2 * inch, f"Acknowledgement: {acknowledgement}")
