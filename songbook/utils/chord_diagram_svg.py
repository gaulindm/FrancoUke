"""
SVG-based chord diagram rendering utilities.
Handles building and rendering chord diagrams as SVG graphics.
"""

from typing import Any, Dict, List
from reportlab.graphics.shapes import Drawing, String, Line, Circle, Rect, Group
from reportlab.graphics import renderSVG
from reportlab.lib import colors


# Constants
STRING_SPACING = 15
FRET_SPACING = 15
DOT_RADIUS = 4
FRET_COUNT = 5


def compute_base_fret(positions: List[Any]) -> int:
    """
    Determine the base fret for the diagram.
    - If any string is open (0) we prefer base fret 1.
    - Otherwise compute the minimum positive fret, and if <= 3 use 1 for readability.
    """
    fretted = [f for f in positions if isinstance(f, int) and f > 0]
    if not fretted:
        return 1
    min_fret = min(fretted)
    return min_fret if min_fret > 3 else 1


def normalize_variation(variation: Any) -> Dict[str, Any]:
    """
    Convert either old-style list [pos,...] or new-style dict into:
    { "positions": [...], "baseFret": int, "barre": { ... } | None }
    """
    if isinstance(variation, dict):
        positions = variation.get("positions", [])
        base = variation.get("baseFret", compute_base_fret(positions))
        barre = variation.get("barre")
        return {"positions": positions, "baseFret": base, "barre": barre}
    
    # Assume iterable positions (old style)
    positions = list(variation) if isinstance(variation, (list, tuple)) else []
    base = compute_base_fret(positions)
    return {"positions": positions, "baseFret": base, "barre": None}


def build_chord_drawing(
    chord_name: str,
    variation: Dict[str, Any],
    scale: float = 1.0,
    instrument: str = "ukulele",
    is_lefty: bool = False
) -> Drawing:
    """
    Build a ReportLab Drawing object for a chord diagram.
    
    Args:
        chord_name: Display name of the chord (e.g., "C", "C[1]")
        variation: Normalized variation dict with positions, baseFret, barre
        scale: Scaling factor for the diagram
        instrument: Instrument type (currently not used in rendering)
        is_lefty: If True, mirror the diagram horizontally
    
    Returns:
        ReportLab Drawing object
    """
    positions = variation.get("positions", [])
    base_fret = variation.get("baseFret", 1)
    barre = variation.get("barre")

    string_count = len(positions)

    # Spacing
    string_spacing = STRING_SPACING * scale
    fret_spacing = FRET_SPACING * scale
    radius = DOT_RADIUS * scale

    # Padding
    LEFT_PAD = 25 * scale
    RIGHT_PAD = 25 * scale
    TOP_PAD = 10 * scale
    BOTTOM_PAD = 15 * scale

    width = (string_count - 1) * string_spacing
    height = FRET_COUNT * fret_spacing

    drawing_width = LEFT_PAD + width + RIGHT_PAD
    drawing_height = TOP_PAD + height + BOTTOM_PAD

    drawing = Drawing(drawing_width, drawing_height)

    # Base fret text
    if base_fret > 1:
        drawing.add(
            String(
                LEFT_PAD - 25 * scale,
                drawing_height - (TOP_PAD + 15 * scale),
                f"{base_fret}fr",
                fontSize=16 * scale,
            )
        )

    # Shapes group (to be mirrored for lefty mode)
    shapes = Group()

    # Draw strings
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

    # Draw frets
    for f in range(FRET_COUNT + 1):
        y = TOP_PAD + f * fret_spacing
        is_nut = (f == FRET_COUNT and base_fret == 1)
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

    # Draw finger dots
    for i, fret in enumerate(positions):
        if fret <= 0:
            continue

        adjusted = fret - (base_fret - 1)
        if 1 <= adjusted <= FRET_COUNT:
            x = LEFT_PAD + i * string_spacing
            y = TOP_PAD + (FRET_COUNT - adjusted) * fret_spacing + (fret_spacing / 2)
            shapes.add(Circle(x, y, radius, fillColor=colors.black))

    # Draw barre
    if barre and all(k in barre for k in ("fret", "fromString", "toString")):
        adjusted = barre["fret"] - (base_fret - 1)
        if 1 <= adjusted <= FRET_COUNT:
            y_bar = TOP_PAD + (FRET_COUNT - adjusted) * fret_spacing + fret_spacing / 2
            x_start = LEFT_PAD + (barre["fromString"] - 1) * string_spacing - radius
            x_end = LEFT_PAD + (barre["toString"] - 1) * string_spacing + radius

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

    # Open (O) / muted (X) markers — not mirrored
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

    # Left-handed mirroring
    if is_lefty:
        shapes.scale(-1, 1)
        shapes.translate(-drawing_width + 2 * LEFT_PAD, 0)

    drawing.add(shapes)
    return drawing


def render_chord_svg(
    chord_name: str,
    variation: Dict[str, Any],
    instrument: str = "ukulele",
    scale: float = 1.0,
    is_lefty: bool = False
) -> str:
    """
    Render a chord diagram as SVG string.
    
    Args:
        chord_name: Display name of the chord
        variation: Chord variation dictionary
        instrument: Instrument type
        scale: Scaling factor
        is_lefty: Mirror horizontally if True
    
    Returns:
        SVG string representation
    """
    drawing = build_chord_drawing(
        chord_name,
        normalize_variation(variation),
        scale=scale,
        instrument=instrument,
        is_lefty=is_lefty,
    )
    return renderSVG.drawToString(drawing)