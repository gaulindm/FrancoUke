# chord_utils.py
import os
import json
import logging
from typing import List, Dict, Any, Optional

from django.conf import settings

from reportlab.graphics.shapes import Drawing, Group, Line, String, Rect, Circle
from reportlab.graphics import renderSVG
from reportlab.platypus import Flowable
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas

from typing import Any, Dict, List
from reportlab.graphics.shapes import (
    Drawing, String, Line, Circle, Rect, Group
)
from reportlab.graphics import renderSVG
from reportlab.lib import colors
from songbook.utils.transposer import clean_chord

logger = logging.getLogger(__name__)


class ChordDiagram(Flowable):
    def __init__(
        self,
        chord_name: str,
        variation: Dict[str, Any],
        scale: float = 0.5,
        is_lefty: bool = False,
        instrument: str = "ukulele",
    ):
        super().__init__()
        self.chord_name = chord_name
        self.variation = normalize_variation(variation)
        self.scale = scale
        self.is_lefty = is_lefty
        self.instrument = instrument

    def draw(self):
        # `self.canv` will be provided by ReportLab when Flowable placed in canvas context.
        self.canv.saveState()
        self.canv.scale(self.scale, self.scale)
        draw_chord_diagram(
            self.canv,
            0,
            0,
            self.variation,
            chord_name=self.chord_name,
            instrument=self.instrument,
            is_lefty=self.is_lefty,
        )
        self.canv.restoreState()


def load_chords(instrument: str) -> List[Dict[str, Any]]:
    """
    Load chord definitions based on the selected instrument.
    Adds common aliases such as "Cmaj7" -> "CM7".
    Expects chord JSON files at <BASE_DIR>/songbook/chords/<instrument>.json
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
                # ensure instrument is recorded on entry
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
    Returns a sorted list of unique chord names.
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
    secondary_instrument: Optional[str] = None,
    is_printing_alternate_chord: bool = False,
    acknowledgement: str = "",
    rows_needed: int = 1,
    diagram_height: int = 0,
):
    """
    Draw footer chord diagrams for primary (and optional secondary) instruments.
    """
    print("\n" + "="*80)
    print("DRAW_FOOTER CALLED")
    print("is_printing_alternate_chord =", is_printing_alternate_chord)
    print("instrument =", instrument)
    print("secondary_instrument =", secondary_instrument)
    print("TOTAL relevant chords =", len(relevant_chords))
    print("="*80 + "\n")

    page_width, _ = doc.pagesize
    max_per_row = 12 if not secondary_instrument else 6

    # -----------------------------------------------------
    # PREPARE CHORDS (first + optional second variation)
    # -----------------------------------------------------
    def prepare_chords(chords, is_printing_alternate_chord):
        print("ALT?", is_printing_alternate_chord, "VARIATIONS:", len(chords))

        diagrams = []
        for chord in chords:
            display_name = chord.get("requested_name") or chord.get("name") or "?"

            raw = chord.get("variations") or chord.get("variation") or []

            if isinstance(raw, dict):
                variations = [raw]
            elif isinstance(raw, list):
                variations = raw
            else:
                variations = []

            # Always draw first variation
            if len(variations) >= 1:
                diagrams.append({
                    "name": display_name,
                    "variation": normalize_variation(variations[0])
                })

            # Draw alternate if enabled
            if is_printing_alternate_chord and len(variations) >= 2:
                diagrams.append({
                    "name": display_name,
                    "variation": normalize_variation(variations[1])
                })

        return diagrams


    # -----------------------------------------------------
    # SORT CHORDS BY INSTRUMENT
    # -----------------------------------------------------
    primary_diagrams = prepare_chords(
        [ch for ch in relevant_chords if ch.get("instrument") == instrument],
        is_printing_alternate_chord
    )

    secondary_diagrams = prepare_chords(
        [ch for ch in relevant_chords if secondary_instrument and ch.get("instrument") == secondary_instrument],
        is_printing_alternate_chord
    ) if secondary_instrument else []


    # -----------------------------------------------------
    # CALCULATE ROWS NEEDED
    # -----------------------------------------------------
    if secondary_instrument:
        primary_rows = (len(primary_diagrams) + max_per_row - 1) // max_per_row
        secondary_rows = (len(secondary_diagrams) + max_per_row - 1) // max_per_row
        rows_needed = max(primary_rows, secondary_rows)
    else:
        rows_needed = (len(primary_diagrams) + max_per_row - 1) // max_per_row if primary_diagrams else 0

    # -----------------------------------------------------
    # DRAWING UTILITY
    # -----------------------------------------------------
    def draw_diagrams(diagrams: List[Dict[str, Any]], start_x: float, start_y: float, inst: str):
        rows = [diagrams[i:i + max_per_row] for i in range(0, len(diagrams), max_per_row)]
        first_row_y = start_y

        y_offset = start_y - (len(rows) - 1) * row_spacing if rows else start_y

        for row in rows:
            # center diagrams inside quarter width
            x_offset = start_x + (page_width / 4 - len(row) * chord_spacing / 2)

            for chord in row:
                display_name = clean_chord(chord.get("name", ""))
                diagram_var = chord.get("variation", {})

                diag = ChordDiagram(display_name, diagram_var, scale=0.5, is_lefty=is_lefty, instrument=inst)
                diag.canv = canvas

                canvas.saveState()
                canvas.translate(x_offset, y_offset)
                diag.draw()
                canvas.restoreState()

                x_offset += chord_spacing

            y_offset -= row_spacing

        return first_row_y

    # -----------------------------------------------------
    # INITIAL Y POSITION
    # -----------------------------------------------------
    start_y = 34 if rows_needed <= 1 else 172

    # -----------------------------------------------------
    # DRAW PRIMARY AND SECONDARY DIAGRAMS
    # -----------------------------------------------------
    if not secondary_instrument:
        draw_diagrams(primary_diagrams, page_width / 4, start_y, instrument)
    else:
        draw_diagrams(primary_diagrams, page_width / 4 - 140, start_y, instrument)
        draw_diagrams(secondary_diagrams, 3 * page_width / 4 - 140, start_y, secondary_instrument)

        # Labels
        label_y = 96 if rows_needed == 1 else 165
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(page_width / 4, label_y, instrument.title())
        canvas.drawCentredString(3 * page_width / 4, label_y, secondary_instrument.title())

    # -----------------------------------------------------
    # Acknowledgement line
    # -----------------------------------------------------
    if acknowledgement:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawCentredString(
            doc.pagesize[0] / 2,
            0.2 * inch,
            f"Acknowledgement: {acknowledgement}"
        )


# ----------------- Diagram primitives & helpers ----------------- #
def compute_base_fret(positions: List[Any]) -> int:
    """
    Determine the base fret for the diagram.
    - If any string is open (0) we prefer base fret 1.
    - Otherwise compute the minimum positive fret, and if <= 3 use 1 for readability.
    """
    # Filter only integer fret numbers > 0
    fretted = [f for f in positions if isinstance(f, int) and f > 0]
    if not fretted:
        # If there are no fretted notes, base fret is 1
        return 1
    min_fret = min(fretted)
    return min_fret if min_fret > 3 else 1


def detect_barre(positions: List[Any]) -> Optional[Dict[str, int]]:
    """
    Detect a barre if two or more adjacent strings are held at the same positive fret.
    Returns a dict {fromString, toString, fret} or None.
    Strings are 1-indexed left->right (as original JSON format expects).
    """
    n = len(positions)
    i = 0
    while i < n:
        f = positions[i]
        if isinstance(f, int) and f > 0:
            # try to find a run of the same fret
            j = i + 1
            while j < n and positions[j] == f:
                j += 1
            # j-1 is last index with same fret
            if j - i >= 2:
                # found a barre from i..(j-1)
                return {
                    "fromString": i + 1,
                    "toString": j,
                    "fret": f
                }
            i = j
        else:
            i += 1
    return None




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
    Improved left-handed chord diagram support.
    - Correct string mirroring
    - Correct barre mirroring
    - Correct open/muted markers
    - Fixes reversed chord-name issue (display only)
    """

    # 1. Normalize variation
    if isinstance(variation, dict):
        positions = variation.get("positions", [])
        base_fret = variation.get("baseFret", compute_base_fret(positions))
        barre = variation.get("barre")
    else:
        positions = list(variation)
        base_fret = compute_base_fret(positions)
        barre = detect_barre(positions)

    # -----------------------------------------------
    # 2. MIRROR FOR LEFTIES
    # -----------------------------------------------
    if is_lefty:
        positions = list(reversed(positions))

        if barre:
            string_count = len(positions)
            barre = {
                "fromString": (string_count + 1) - barre["toString"],
                "toString": (string_count + 1) - barre["fromString"],
                "fret": barre["fret"],
            }

        # Fix display name (Am stays Am)
        chord_name = clean_chord(chord_name)

    # -----------------------------------------------
    # 3. Adjust frets relative to base-fret
    # -----------------------------------------------
    adjusted_positions = [
        (f - (base_fret - 1) if isinstance(f, int) and f > 0 else f)
        for f in positions
    ]

    string_count = max(1, len(positions))
    fret_count = 5
    string_spacing = 15
    fret_spacing = 15
    radius = 4

    # -----------------------------------------------
    # 4. Draw chord name
    # -----------------------------------------------
    if chord_name:
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(
            x + (string_count - 1) * string_spacing / 2,
            y + fret_count * fret_spacing + 18,
            chord_name
        )

    # -----------------------------------------------
    # 5. Base fret label
    # -----------------------------------------------
    if base_fret > 1:
        # Shift label to mirror side when lefty
        label_x = x - 20 if not is_lefty else x + (string_count - 1) * string_spacing + 5
        c.setFont("Helvetica", 14)
        c.drawString(label_x, y + fret_count * fret_spacing - 10, f"{base_fret}fr")

    # -----------------------------------------------
    # 6. Draw strings
    # -----------------------------------------------
    for i in range(string_count):
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(
            x + i * string_spacing,
            y,
            x + i * string_spacing,
            y + fret_count * fret_spacing
        )

    # -----------------------------------------------
    # 7. Draw frets
    # -----------------------------------------------
    for j in range(fret_count + 1):
        y_line = y + j * fret_spacing
        width = 4 if (j == fret_count and base_fret == 1) else 2
        c.setLineWidth(width)
        c.line(x, y_line, x + (string_count - 1) * string_spacing, y_line)

    # -----------------------------------------------
    # 8. Draw barre
    # -----------------------------------------------
    if barre:
        adj_fret = barre["fret"] - (base_fret - 1)
        if 1 <= adj_fret <= fret_count:
            start = barre["fromString"] - 1
            end = barre["toString"] - 1
            y_bar = y + (fret_count - adj_fret) * fret_spacing + fret_spacing / 2
            x_start = x + start * string_spacing - radius
            width = (end - start) * string_spacing + 2 * radius
            c.setFillColor(colors.black)
            c.roundRect(x_start, y_bar - radius, width, 2 * radius, 2, stroke=0, fill=1)

    # -----------------------------------------------
    # 9. Draw fretted dots + muted/open strings
    # -----------------------------------------------
    for i, fret in enumerate(adjusted_positions):
        x_dot = x + i * string_spacing

        if isinstance(fret, int) and fret > 0:
            y_dot = y + (fret_count - fret) * fret_spacing + fret_spacing / 2
            c.setFillColor(colors.black)
            c.circle(x_dot, y_dot, radius, stroke=0, fill=1)
        else:
            if instrument == "guitar":
                if fret == 0:
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(x_dot, y + fret_count * fret_spacing + 5, "O")
                elif fret == -1:
                    c.setFont("Helvetica", 11)
                    c.drawCentredString(x_dot, y + fret_count * fret_spacing + 4, "X")

from typing import Any, Dict, List
from reportlab.graphics.shapes import (
    Drawing, String, Line, Circle, Rect, Group
)
from reportlab.graphics import renderSVG
from reportlab.lib import colors


# ------------------------------------------------------
# NORMALIZE VARIATION INPUT
# ------------------------------------------------------
def normalize_variation_svg(variation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures variation keys are always consistent:
    - positions: list of ints per string
    - baseFret: int
    - barre: {fret, fromString, toString} or None
    """
    return {
        "positions": variation.get("positions", []),
        "baseFret": variation.get("baseFret", 1),
        "barre": variation.get("barre"),
    }


def normalize_variation(variation: Any) -> Dict[str, Any]:
    """
    Convert either old-style list [pos,...] or new-style dict into:
    { "positions": [...], "baseFret": int, "barre": { ... } | None }
    """
    if isinstance(variation, dict):
        # Ensure keys exist and compute missing ones
        positions = variation.get("positions", [])
        base = variation.get("baseFret", compute_base_fret(positions))
        barre = variation.get("barre") or detect_barre(positions)
        return {"positions": positions, "baseFret": base, "barre": barre}
    # assume iterable positions (old style)
    positions = list(variation) if isinstance(variation, (list, tuple)) else []
    base = compute_base_fret(positions)
    barre = detect_barre(positions)
    return {"positions": positions, "baseFret": base, "barre": barre}


# ------------------------------------------------------
# BUILD CHORD DRAWING
# ------------------------------------------------------
def build_chord_drawing(
    chord_name: str,
    variation: Dict[str, Any],
    scale: float = 1.0,
    instrument: str = "ukulele",
    is_lefty: bool = False
):
    positions = variation.get("positions", [])
    base_fret = variation.get("baseFret", 1)
    barre = variation.get("barre")

    fret_count = 5
    string_count = len(positions)

    # Spacing
    string_spacing = 15 * scale
    fret_spacing   = 15 * scale
    radius         = 4 * scale

    # Padding
    LEFT_PAD = 25 * scale
    RIGHT_PAD = 25 * scale
    TOP_PAD = 10 * scale
    BOTTOM_PAD = 15 * scale

    width  = (string_count - 1) * string_spacing
    height = fret_count * fret_spacing

    drawing_width  = LEFT_PAD + width + RIGHT_PAD
    drawing_height = TOP_PAD + height + BOTTOM_PAD

    drawing = Drawing(drawing_width, drawing_height)

    # ------------------------------------------------------
    # BASE FRET TEXT
    # ------------------------------------------------------
    if base_fret > 1:
        drawing.add(
            String(
                LEFT_PAD - 25 * scale,
                drawing_height - (TOP_PAD + 15 * scale),
                f"{base_fret}fr",
                fontSize=16 * scale,
            )
        )

    # ------------------------------------------------------
    # SHAPES GROUP (TO BE MIRRORED FOR LEFTY MODE)
    # ------------------------------------------------------
    shapes = Group()

    # --- Strings ---
    for i in range(string_count):
        x = LEFT_PAD + i * string_spacing
        shapes.add(
            Line(
                x,
                TOP_PAD,
                x,
                TOP_PAD + height,
                strokeColor=colors.black,
                strokeWidth=2 * scale,
            )
        )

    # --- Frets ---
    for f in range(fret_count + 1):
        y = TOP_PAD + f * fret_spacing

        # Nut only if base fret == 1
        is_nut = (f == fret_count and base_fret == 1)
        stroke = 5 * scale if is_nut else 2 * scale

        shapes.add(
            Line(
                LEFT_PAD,
                y,
                LEFT_PAD + width,
                y,
                strokeColor=colors.black,
                strokeWidth=stroke,
            )
        )

    # --- Finger Dots ---
    for i, fret in enumerate(positions):
        if fret <= 0:
            continue

        adjusted = fret - (base_fret - 1)
        if 1 <= adjusted <= fret_count:
            x = LEFT_PAD + i * string_spacing
            y = TOP_PAD + (fret_count - adjusted) * fret_spacing + (fret_spacing / 2)
            shapes.add(Circle(x, y, radius, fillColor=colors.black))

    # --- Barre ---
    if barre and all(k in barre for k in ("fret", "fromString", "toString")):
        adjusted = barre["fret"] - (base_fret - 1)
        if 1 <= adjusted <= fret_count:

            y_bar = TOP_PAD + (fret_count - adjusted) * fret_spacing + fret_spacing / 2
            x_start = LEFT_PAD + (barre["fromString"] - 1) * string_spacing - radius
            x_end   = LEFT_PAD + (barre["toString"] - 1) * string_spacing + radius

            shapes.add(
                Rect(
                    x_start,
                    y_bar - radius,
                    x_end - x_start,
                    2 * radius,
                    fillColor=colors.black,
                    strokeColor=None,
                )
            )

    # ------------------------------------------------------
    # OPEN (O) / MUTED (X) MARKERS — NOT MIRRORED
    # ------------------------------------------------------
    nut_offset = 8 * scale
    label_y = drawing_height - TOP_PAD + nut_offset - 8

    for i, fret in enumerate(positions):
        x = LEFT_PAD + i * string_spacing

        if fret == 0:
            drawing.add(
                String(
                    x,
                    label_y,
                    "O",
                    fontSize=12 * scale,
                    textAnchor="middle",
                )
            )

        elif fret < 0:
            drawing.add(
                String(
                    x,
                    label_y,
                    "X",
                    fontSize=12 * scale,
                    textAnchor="middle",
                )
            )

    # ------------------------------------------------------
    # LEFT-HANDED MIRRORING
    # ------------------------------------------------------
    if is_lefty:
        shapes.scale(-1, 1)

        # Proper horizontal correction:
        # We want LEFT_PAD to become RIGHT_PAD after reflecting
        shapes.translate(-drawing_width + 2 * LEFT_PAD, 0)

    drawing.add(shapes)
    return drawing


# ------------------------------------------------------
# RENDER TO SVG
# ------------------------------------------------------
def render_chord_svg(
    chord_name: str,
    variation: Dict[str, Any],
    instrument: str = "ukulele",
    scale: float = 1.0,
    is_lefty: bool = False
) -> str:
    drawing = build_chord_drawing(
        chord_name,
        normalize_variation_svg(variation),
        scale=scale,
        instrument=instrument,
        is_lefty=is_lefty,
    )
    return renderSVG.drawToString(drawing)

