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


# Friendly display labels for instrument tags, used only to distinguish
# stacked chord-diagram blocks in the footer when a secondary instrument
# is set (e.g. "GCEA" vs "Baritone" both showing a "C" chord).
INSTRUMENT_LABELS = {
    "ukulele": "GCEA",
    "baritone": "Baritone",
    "baritone_ukulele": "Baritone",
    "guitar": "Guitar",
    "banjo": "Banjo",
    "mandolin": "Mandolin",
}


def _instrument_label(instrument: str) -> str:
    """
    Human-friendly label for an instrument code. Looks up INSTRUMENT_LABELS
    first; if a new instrument code is added there without updating that
    dict, falls back to turning "baritone_ukulele" into "Baritone Ukulele"
    rather than leaving underscores in the printed label.
    """
    if not instrument:
        return ""
    return INSTRUMENT_LABELS.get(instrument, instrument.replace("_", " ").title())


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


def _chunk_into_rows(diagrams: List[Dict[str, Any]], available_width: float, chord_spacing: int):
    """
    Given a flat list of diagrams, figure out how many fit per row within
    available_width, then chunk into rows. Shared by the primary and
    secondary instrument blocks so both wrap consistently within their
    own column.
    """
    if not diagrams:
        return [], 0

    max_possible_per_row = len(diagrams)
    while (max_possible_per_row - 1) * chord_spacing > available_width * 0.9 and max_possible_per_row > 1:
        max_possible_per_row -= 1

    rows = [diagrams[i:i + max_possible_per_row] for i in range(0, len(diagrams), max_possible_per_row)]
    return rows, max_possible_per_row


LABEL_CLEARANCE = 64  # fixed points of clearance above a diagram's origin
                       # reserved for its instrument label. This is a fixed
                       # value (not row_spacing-relative) because it needs to
                       # clear the diagram's own rendered height, which scale
                       # affects but row_spacing does not. Tune this up if the
                       # label still gets covered, or down if it floats too
                       # far above the diagram.


def _draw_diagram_rows(canvas, rows, start_y, center_x, chord_spacing, row_spacing, is_lefty, instrument, label=None):
    """
    Draw a stack of chord-diagram rows for a single instrument, centered
    on center_x (so a column can be positioned anywhere across the page),
    optionally preceded by a small instrument label. Returns the y
    position just below the last row drawn.
    """
    y_offset = start_y

    if label:
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(center_x, y_offset + LABEL_CLEARANCE, label)
        canvas.setFillColor(colors.black)

    for row in rows:
        row_width = (len(row) - 1) * chord_spacing
        x_offset = center_x - row_width / 2  # center row on center_x

        for chord in row:
            display_name = clean_chord(chord.get("name", ""))
            diagram_var = chord.get("variation", {})

            diag = ChordDiagram(
                display_name,
                diagram_var,
                scale=0.5,
                is_lefty=is_lefty,
                instrument=instrument,
            )
            diag.canv = canvas

            canvas.saveState()
            canvas.translate(x_offset, y_offset)
            diag.draw()
            canvas.restoreState()

            x_offset += chord_spacing

        y_offset -= row_spacing

    return y_offset


def plan_footer_rows(relevant_chords, instrument, secondary_instrument, chord_spacing, page_width,
                      is_printing_alternate_chord=False):
    """
    Work out chord-diagram rows and column layout for the footer, without
    touching a canvas. Shared by draw_footer() (which actually draws) and
    compute_footer_min_bottom_margin() (which sizes the page's bottom
    margin before the document is built), so the two can never disagree
    about how many rows the footer will need.

    Returns (primary_rows, secondary_rows, has_both, left_center_x, right_center_x).
    """
    primary_chords = [ch for ch in relevant_chords if ch.get("instrument") == instrument]
    primary_diagrams = prepare_chords(primary_chords, is_printing_alternate_chord)

    secondary_diagrams = []
    if secondary_instrument and secondary_instrument != instrument:
        secondary_chords = [ch for ch in relevant_chords if ch.get("instrument") == secondary_instrument]
        secondary_diagrams = prepare_chords(secondary_chords, is_printing_alternate_chord)

    has_both = bool(primary_diagrams) and bool(secondary_diagrams)

    if has_both:
        column_margin = chord_spacing * 0.5
        column_width = page_width / 2 - column_margin
        left_center_x = page_width / 4
        right_center_x = page_width * 3 / 4
    else:
        column_width = page_width
        left_center_x = right_center_x = page_width / 2

    primary_rows, _ = _chunk_into_rows(primary_diagrams, column_width, chord_spacing)
    secondary_rows, _ = _chunk_into_rows(secondary_diagrams, column_width, chord_spacing)

    return primary_rows, secondary_rows, has_both, left_center_x, right_center_x


def compute_footer_min_bottom_margin(relevant_chords, instrument, secondary_instrument, chord_spacing,
                                      row_spacing, page_width, is_printing_alternate_chord=False,
                                      extra_padding=20, fallback=80):
    """
    Compute the minimum SimpleDocTemplate bottomMargin needed so the
    footer's chord diagrams never overlap the song's lyrics.

    IMPORTANT: call this BEFORE constructing SimpleDocTemplate, using the
    same relevant_chords, chord_spacing, and row_spacing that will later be
    passed to draw_footer() in onFirstPage/onLaterPages. bottomMargin can't
    be changed after the doc starts laying out flowables — with more chords
    the footer grows to two (or more) rows and needs more reserved space,
    otherwise ReportLab lays lyrics out assuming a fixed, smaller margin
    and the last lines of text get drawn underneath the diagrams.

    extra_padding adds breathing room above the tallest row (and its label,
    if there is one) so the last line of lyrics isn't flush against the
    chord diagrams. fallback is returned when there's nothing to draw, so
    callers can pass this straight into bottomMargin= without a None-check.
    """
    primary_rows, secondary_rows, has_both, _, _ = plan_footer_rows(
        relevant_chords, instrument, secondary_instrument, chord_spacing, page_width,
        is_printing_alternate_chord,
    )

    if not primary_rows and not secondary_rows:
        return fallback

    ack_height = 20
    bottom_margin = 10 + ack_height
    bottom_margin_safe = bottom_margin + ack_height

    rows_needed = max(len(primary_rows), len(secondary_rows))
    total_rows_height = rows_needed * row_spacing
    start_y = bottom_margin_safe + total_rows_height - row_spacing - 10

    footer_top = start_y + (LABEL_CLEARANCE if has_both else 0)
    return max(fallback, footer_top + extra_padding)


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
    revision_date: str = "",
):
    """
    Draw footer chord diagrams, dynamically adjusting number per row and
    vertical position. When a secondary_instrument is set, its chords are
    drawn as a second, labeled block stacked above the primary block.
    """

    page_width, page_height = canvas._pagesize
    ack_height = 20
    bottom_margin = 10 + ack_height
    bottom_margin_safe = bottom_margin + ack_height

    # Row/column planning is shared with compute_footer_min_bottom_margin()
    # so the doc's bottomMargin (set before the page even exists) always
    # agrees with what actually gets drawn here.
    primary_rows, secondary_rows, has_both, left_center_x, right_center_x = plan_footer_rows(
        relevant_chords, instrument, secondary_instrument, chord_spacing, page_width,
        is_printing_alternate_chord,
    )

    if not primary_rows and not secondary_rows:
        return

    # The two columns are drawn side by side, so the footer only needs to be
    # as tall as the taller of the two column's row stacks. This is the same
    # formula regardless of has_both, so the diagrams sit at the same height
    # whether there's one instrument or two — the label (when present) is
    # drawn in the fixed LABEL_CLEARANCE gap above the top row rather than
    # by inflating this block's height, so it never pushes the diagrams up.
    rows_needed = max(len(primary_rows), len(secondary_rows))
    total_rows_height = rows_needed * row_spacing

    # Start drawing the top-most row just above the bottom safe margin.
    start_y = bottom_margin_safe + total_rows_height - row_spacing - 10

    if primary_rows:
        label = _instrument_label(instrument) if has_both else None
        _draw_diagram_rows(
            canvas, primary_rows, start_y, left_center_x, chord_spacing, row_spacing,
            is_lefty, instrument, label=label,
        )

    if secondary_rows:
        label = _instrument_label(secondary_instrument) if has_both else None
        _draw_diagram_rows(
            canvas, secondary_rows, start_y, right_center_x, chord_spacing, row_spacing,
            is_lefty, secondary_instrument, label=label,
        )

    # -------------------------
    # Draw acknowledgement (+ revision date, in parentheses, if present)
    # -------------------------
    if acknowledgement and revision_date:
        footer_line = f"Acknowledgement: {acknowledgement} ({revision_date})"
    elif acknowledgement:
        footer_line = f"Acknowledgement: {acknowledgement}"
    elif revision_date:
        footer_line = f"({revision_date})"
    else:
        footer_line = ""

    if footer_line:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(page_width / 2, bottom_margin - ack_height / 2, footer_line)