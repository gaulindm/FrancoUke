#chord_utils.py
import os
import json
from django.conf import settings
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Spacer, Flowable
from reportlab.lib import colors
from reportlab.lib.units import inch




from reportlab.platypus import Flowable

class ChordDiagram(Flowable):
    def __init__(self, chord_name, variation, scale=0.5, is_lefty=False, instrument="ukulele"):
        super().__init__()
        self.chord_name = chord_name
        self.variation = normalize_variation(variation)
        self.scale = scale
        self.is_lefty = is_lefty
        self.instrument = instrument  # NEW: store instrument

    def draw(self):
        self.canv.saveState()
        self.canv.scale(self.scale, self.scale)
        draw_chord_diagram(
            self.canv,
            0,
            0,
            self.variation,
            self.chord_name,
            instrument=self.instrument  # pass instrument down
        )
        self.canv.restoreState()


def load_chords(instrument):
    """
    Load chord definitions based on the selected instrument.
    """
    # Point to the songbook/chords folder instead of static/js
    chords_dir = os.path.join(settings.BASE_DIR, 'songbook', 'chords')
    
    file_map = {
        'ukulele': os.path.join(chords_dir, 'ukulele.json'),
        'guitar': os.path.join(chords_dir, 'guitar.json'),
        'guitalele': os.path.join(chords_dir, 'guitalele.json'),
        'mandolin': os.path.join(chords_dir, 'mandolin.json'),
        'banjo': os.path.join(chords_dir, 'banjo.json'),
        'baritone_ukulele': os.path.join(chords_dir, 'baritoneUke.json'),
    }

    file_path = file_map.get(instrument, file_map['ukulele'])
    print(f"DEBUG: Loading chords for instrument '{instrument}' from {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            chords = json.load(file)
            print(f"DEBUG: Loaded {len(chords)} chords for {instrument}")
            # Ensure instrument field exists
            for chord in chords:
                chord["instrument"] = instrument
            return chords
    except FileNotFoundError:
        print(f"ERROR: Chord file not found for {instrument} at {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON format in {file_path}: {e}")
        return []


    
def extract_used_chords(lyrics_with_chords):
    """
    Extract chord names from the lyrics_with_chords JSON structure.
    Handles nested lists and dictionaries containing 'chord' keys.
    """
    chords = set()  # Use a set to avoid duplicates

    def traverse_structure(data):
        """
        Traverse through the JSON structure to find and collect chords.
        """
        if isinstance(data, dict):
            # Check if this dictionary contains a 'chord' key
            if "chord" in data and data["chord"]:
                chords.add(data["chord"])  # Add the chord to the set
            # Recursively check other values in the dictionary
            for value in data.values():
                traverse_structure(value)
        elif isinstance(data, list):
            # Traverse each item in the list
            for item in data:
                traverse_structure(item)

    # Start traversing the provided JSON structure
    traverse_structure(lyrics_with_chords)

    # Debug: Print collected chords
    #print("Extracted chords:", chords)

    # Return the chords as a sorted list
    return sorted(chords)


def draw_footer(canvas, doc, relevant_chords, chord_spacing, row_spacing, 
                 is_lefty, instrument="ukulele", secondary_instrument=None,
                 is_printing_alternate_chord=False, acknowledgement='',
                 rows_needed=1, diagram_height=0):
    
    #print(f"DEBUG: draw_footer called with instrument='{instrument}', secondary_instrument='{secondary_instrument}'")
    #print(f"DEBUG: relevant_chords count = {len(relevant_chords)}")

    page_width, _ = doc.pagesize
    max_per_row = 12 if not secondary_instrument else 6

    def prepare_chords(chords):
        diagrams = []
        for chord in chords:
            #print(f"DEBUG: Preparing chord '{chord.get('name')}' for instrument '{chord.get('instrument')}'")
            diagrams.append({
                "name": chord["name"],
                "variation": chord["variations"][0]
            })
            if is_printing_alternate_chord and len(chord["variations"]) > 1:
                diagrams.append({
                    "name": chord["name"],
                    "variation": chord["variations"][1]
                })
        return diagrams

    primary_diagrams = prepare_chords(
        [chord for chord in relevant_chords if chord.get("instrument") == instrument]
    )
    #print(f"DEBUG: primary_diagrams count = {len(primary_diagrams)}")

    secondary_diagrams = prepare_chords(
        [chord for chord in relevant_chords if secondary_instrument and chord.get("instrument") == secondary_instrument]
    )
    #print(f"DEBUG: secondary_diagrams count = {len(secondary_diagrams)}")

    if secondary_instrument:
        primary_rows = (len(primary_diagrams) + max_per_row - 1) // max_per_row
        secondary_rows = (len(secondary_diagrams) + max_per_row - 1) // max_per_row
        rows_needed = max(primary_rows, secondary_rows)
    else:
        rows_needed = (len(primary_diagrams) + max_per_row - 1) // max_per_row

    #print(f"DEBUG: rows_needed = {rows_needed}")





    def draw_diagrams(diagrams, start_x, start_y):
        rows = [diagrams[i:i + max_per_row] for i in range(0, len(diagrams), max_per_row)]
        
        first_row_y = start_y  # Capture the original top position
        
        y_offset = start_y - (len(rows) - 1) * row_spacing  # Adjust for multiple rows
        
        for row in rows:
            x_offset = start_x + (page_width / 4 - len(row) * chord_spacing / 2)
            for chord in row:
                diagram = ChordDiagram(chord["name"], chord["variation"], scale=0.5, is_lefty=is_lefty)
                diagram.canv = canvas
                canvas.saveState()
                canvas.translate(x_offset, y_offset)
                diagram.draw()
                canvas.restoreState()
                x_offset += chord_spacing
            y_offset -= row_spacing

        return first_row_y  # Always return the original start position
    

    start_y = 34 if rows_needed == 1 else 172
    #print(f"DEBUG: start_y calculated from pdf_generator {start_y}")
    if not secondary_instrument:
        label_y = draw_diagrams(primary_diagrams, page_width / 4, start_y)
    else:
        label_y = draw_diagrams(primary_diagrams, page_width / 4 - 140, start_y)
        draw_diagrams(secondary_diagrams, 3 * page_width / 4 - 140, start_y)



    

    if secondary_instrument:
        label_y = 96 if rows_needed == 1 else 165  # Keep it simple!
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(page_width / 4, label_y, instrument.title())
        if secondary_instrument:
            canvas.drawCentredString(3 * page_width / 4, label_y, secondary_instrument.title())


#Acknowledgment 
    if acknowledgement:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawCentredString(
            doc.pagesize[0] / 2, 0.2 * inch,  #changer .5 a .25
            f"Ackowledgement: {acknowledgement}"
        )
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# --- Helper Functions ---
def compute_base_fret(positions):
    """Determine the base fret for the diagram."""
    if any(f == 0 for f in positions):
        return 1
    fretted = [f for f in positions if isinstance(f, int) and f > 0]
    if not fretted:
        return 1
    min_fret = min(fretted)
    return min_fret if min_fret > 3 else 1

def normalize_variation(variation):
    """Return a modern variation object: {positions, baseFret, barre}."""
    if isinstance(variation, dict):
        # already modern
        return variation
    # old style → wrap
    return {
        "positions": variation,
        "baseFret": compute_base_fret(variation),
        "barre": detect_barre(variation)
    }


def detect_barre(positions):
    """Detects a barre (two or more adjacent strings at the same fret)."""
    i = 0
    while i < len(positions):
        fret = positions[i]
        if fret > 0:
            start = i
            while i + 1 < len(positions) and positions[i + 1] == fret:
                i += 1
            if i > start:
                return {
                    "fromString": start + 1,
                    "toString": i + 1,
                    "fret": fret
                }
        i += 1
    return None

def draw_chord_diagram(c, x, y, variation, chord_name="", instrument="ukulele"):
    """
    Draw a chord diagram. Only guitar diagrams show muted/open string markers.
    """
    # Normalize variation
    if isinstance(variation, dict):
        positions = variation.get("positions", [])
        base_fret = variation.get("baseFret", compute_base_fret(positions))
        barre = variation.get("barre")
    else:
        positions = variation
        base_fret = compute_base_fret(positions)
        barre = detect_barre(positions)

    adjusted_positions = [
        (f - (base_fret - 1) if f > 0 else f)
        for f in positions
    ]

    string_count = len(positions)
    fret_count = 5
    string_spacing = 15
    fret_spacing = 15
    radius = 4

    # Chord name
    if chord_name:
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(
            x + (string_count - 1) * string_spacing / 2,
            y + fret_count * fret_spacing + 18,
            chord_name
        )

    # Base fret
    if base_fret > 1:
        c.setFont("Helvetica", 14)
        c.drawString(x - 20, y + fret_count * fret_spacing - 10, f"{base_fret}fr")

    # Strings
    for i in range(string_count):
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(x + i * string_spacing, y, x + i * string_spacing, y + fret_count * fret_spacing)

    # Frets
    for j in range(fret_count + 1):
        y_line = y + j * fret_spacing
        c.setLineWidth(4 if (j == fret_count and base_fret == 1) else 2)
        c.line(x, y_line, x + (string_count - 1) * string_spacing, y_line)

    # Barre
    if barre:
        adj_fret = barre["fret"] - (base_fret - 1)
        if 1 <= adj_fret <= fret_count:
            start_string = barre["fromString"] - 1
            end_string = barre["toString"] - 1
            y_bar = y + (fret_count - adj_fret) * fret_spacing + fret_spacing / 2
            x_start = x + start_string * string_spacing - radius
            width = (end_string - start_string) * string_spacing + 2 * radius
            c.setFillColor(colors.black)
            c.roundRect(x_start, y_bar - radius, width, 2 * radius, 2, stroke=0, fill=1)

    # Dots + markers
    for i, fret in enumerate(adjusted_positions):
        x_dot = x + i * string_spacing
        if fret > 0:
            y_dot = y + (fret_count - fret) * fret_spacing + fret_spacing / 2
            c.setFillColor(colors.black)
            c.circle(x_dot, y_dot, radius, stroke=0, fill=1)
        elif instrument == "guitar":
            if fret == 0:
                c.setFont("Helvetica", 12)
                c.drawCentredString(x_dot, y + fret_count * fret_spacing + 5, "O")
            elif fret == -1:
                c.setFont("Helvetica", 11)
                c.drawCentredString(x_dot, y + fret_count * fret_spacing + 4, "X")
