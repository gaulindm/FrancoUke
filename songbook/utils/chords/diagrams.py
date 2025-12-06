# diagrams.py
from reportlab.platypus import Flowable
from reportlab.graphics.shapes import Drawing, Group, Line, Circle, Rect, String
from reportlab.graphics import renderSVG
from reportlab.lib import colors
from typing import Dict, Any
from .normalize import normalize_variation
from typing import List, Dict, Any, Optional


class ChordDiagram(Flowable):
    """
    Flowable class for embedding chord diagrams in ReportLab documents.
    Debug version with extra prints and guaranteed simple square if nothing is drawn.
    """
    def __init__(
        self,
        chord_name: str,
        variation: Dict[str, Any],
        scale: float = 0.2,
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
        c = self.canv
        c.saveState()
        c.scale(self.scale, self.scale)

        positions = self.variation.get("positions", [])
        base_fret = self.variation.get("baseFret", 1)
        barre = self.variation.get("barre")

        # Debug prints
        print(f"[DEBUG] Drawing chord '{self.chord_name}' at scale={self.scale}")
        print(f"        positions={positions}, baseFret={base_fret}, barre={barre}, is_lefty={self.is_lefty}")

        # Mirror for lefties
        if self.is_lefty:
            positions = list(reversed(positions))
            if barre:
                string_count = len(positions)
                barre = {
                    "fromString": (string_count + 1) - barre["toString"],
                    "toString": (string_count + 1) - barre["fromString"],
                    "fret": barre["fret"],
                }

        # Adjust positions relative to base fret
        adjusted_positions = [(f - (base_fret - 1) if isinstance(f, int) and f > 0 else f)
                              for f in positions]

        string_count = max(1, len(positions))
        fret_count = 5
        dot_radius = 4

        # Draw a simple fallback rectangle (always visible)
        c.setStrokeColor(colors.red)
        c.setLineWidth(1)
        c.rect(0, 0, (string_count - 1) * 15, fret_count * 15)




        # Draw strings
        c.setStrokeColor(colors.black)
        for i in range(string_count):
            c.line(i * 15, 0, i * 15, fret_count * 15)

        # Draw frets
        for j in range(fret_count + 1):
            # Only draw thick nut bar when baseFret is 1 (no offset)
            width = 4 if (j == fret_count and base_fret == 1) else 1
            c.setLineWidth(width)
            c.line(0, j * 15, (string_count - 1) * 15, j * 15)

        # Draw barre if specified
        if barre:
            adj_fret = barre["fret"] - (base_fret - 1)
            if 1 <= adj_fret <= fret_count:
                start = barre["fromString"] - 1
                end = barre["toString"] - 1
                y_bar = (fret_count - adj_fret) * 15 + 15 / 2
                x_start = start * 15 - dot_radius
                width = (end - start) * 15 + 2 * dot_radius
                c.setFillColor(colors.black)
                c.roundRect(x_start, y_bar - dot_radius, width, 2 * dot_radius, 2, stroke=0, fill=1)

        # Draw dots for each finger position
        for i, fret in enumerate(adjusted_positions):
            x_dot = i * 15
            if isinstance(fret, int) and fret > 0:
                y_dot = (fret_count - fret) * 15 + 15 / 2
                c.setFillColor(colors.black)
                c.circle(x_dot, y_dot, dot_radius, stroke=0, fill=1)
            elif fret == 0:
                c.setFont("Helvetica", 10)
                c.drawCentredString(x_dot, fret_count * 15 + 5, "O")
            elif fret == -1:
                c.setFont("Helvetica", 10)
                c.drawCentredString(x_dot, fret_count * 15 + 5, "X")

        # Draw chord name
        label_name = self.chord_name
        if self.variation_index is not None:
            label_name += f"[{self.variation_index}]"
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString((string_count - 1) * 15 / 2, fret_count * 15 + 18, label_name)

        # 🆕 Draw base fret number if > 1 (at the TOP of the diagram)
        if base_fret > 1:
            c.setFont("Helvetica", 14)
            # Position it to the left of the TOP fret line
            c.drawRightString(-5, fret_count * 15 - 12, f"{base_fret}fr")



        c.restoreState()


def draw_chord_diagram(c, x: float, y: float, variation: Dict[str, Any], chord_name: str = "", instrument: str = "ukulele", is_lefty: bool = False):
    positions = variation.get("positions", [])
    base_fret = variation.get("baseFret", 1)
    barre = variation.get("barre")
    fret_count = 5
    string_count = len(positions)
    string_spacing = 15
    fret_spacing = 15
    radius = 4

    # Draw strings, frets, barre, finger dots, etc.
    # (Use your previous implementation here)
    # ...
    # (Omitted for brevity; same as chord_utils.py)

def build_chord_drawing(chord_name: str, variation: Dict[str, Any], scale: float = 1.0, instrument: str = "ukulele", is_lefty: bool = False):
    drawing = Drawing(100, 100)  # placeholder; copy previous full implementation
    return drawing
