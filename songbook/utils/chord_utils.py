
import os
import json
from django.conf import settings
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Spacer, Flowable
from reportlab.lib import colors
from reportlab.lib.units import inch

class ChordDiagram(Flowable):
    def __init__(self, chord_name, variation, scale=0.5, is_lefty=False):
        super().__init__()
        self.chord_name = chord_name
        self.variation = variation  # e.g., [0, 0, 0, 3]
        self.scale = scale
        self.is_lefty = is_lefty  # New parameter to handle left-handed diagrams

    def draw(self):
        string_spacing = 15 * self.scale
        fret_spacing = 15 * self.scale
        num_frets = 5
        num_strings = len(self.variation)

        # Detect if the chord needs an offset (all non-open frets above the 3rd fret)
        non_open_frets = [fret for fret in self.variation if fret > 0]
        min_fret = min(non_open_frets, default=0)  # Use default=0 if no valid frets
        needs_offset = min_fret > 3

        # Calculate offset
        fret_offset = min_fret - 1 if needs_offset else 0

        # Flip x-coordinates if lefty
        def flip_x(x):
            return (num_strings - 1) * string_spacing - x if self.is_lefty else x

        # Draw nut or offset label
        if needs_offset:
            self.canv.setFont("Helvetica-Bold", 10)  # Slightly larger font
            self.canv.setFillColor(colors.red)  # Use a distinct color
            self.canv.drawString(-15, fret_spacing * (num_frets - 1) + 5, f"{fret_offset}")
            self.canv.setFillColor(colors.black)  # Reset color for other elements
        else:
            self.canv.setLineWidth(2)
            self.canv.line(0, fret_spacing * num_frets, string_spacing * (num_strings - 1), fret_spacing * num_frets)
            self.canv.setLineWidth(1)

        # Draw strings
        for i in range(num_strings):
            x = flip_x(i * string_spacing)
            self.canv.line(x, 0, x, fret_spacing * num_frets)

        # Draw frets
        for i in range(num_frets + 1):
            y = i * fret_spacing
            self.canv.line(0, y, string_spacing * (num_strings - 1), y)

        # Draw chord name
        self.canv.setFont("Helvetica-Bold", 12)
        self.canv.drawCentredString(
            (num_strings - 1) * string_spacing / 2,
            fret_spacing * (num_frets + 1)+2,
            self.chord_name
        )

        # Calculate max height for y-axis flipping
        max_height = num_frets * fret_spacing

        # Draw finger positions (dots)
        self.canv.setFillColor(colors.black)
        for string_idx, fret in enumerate(self.variation):
            if fret > 0:  # Ignore open strings
                adjusted_fret = fret - fret_offset
                if adjusted_fret > 0:  # Only draw if the fret is within the diagram
                    x = flip_x(string_idx * string_spacing)
                    y = max_height - ((adjusted_fret - 0.5) * fret_spacing)
                    self.canv.circle(x, y, 4 * self.scale, fill=1)

        # Draw open strings
        self.canv.setFillColor(colors.white)
        self.canv.setStrokeColor(colors.black)
        for string_idx, fret in enumerate(self.variation):
            if fret == 0:  # Open string
                x = flip_x(string_idx * string_spacing)
                y = max_height + 5  # Position above the first fret
                self.canv.circle(x, y, 4 * self.scale, fill=1)



def load_chords(instrument):
    """
    Load chord definitions based on the selected instrument.
    """
    # Dynamically locate the directory where chord files are stored
    #base_dir = os.path.dirname(os.path.abspath(__file__))  # Current file's directory
    #chord_files_dir = os.path.join(base_dir, '..', 'chord_definitions')  # Adjust path
    static_dir = os.path.join(settings.BASE_DIR, 'static', 'js')  # Adjust path for static location


    file_map = {
        'ukulele': os.path.join(static_dir, 'ukulele_chords.json'),
        'guitar': os.path.join(static_dir, 'guitar_chords.json'),
        'mandolin': os.path.join(static_dir, 'mandolin_chords.json'),
        "banjo": os.path.join(static_dir, "banjo_chords.json"),
        "baritone_ukulele": os.path.join(static_dir, "baritoneUke_chords.json"),
    }

    file_path = file_map.get(instrument, file_map['ukulele'])  # Default to ukulele
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        #print(f"Error: Chord file not found for {instrument}")
        return []
    except json.JSONDecodeError as e:
        #print(f"Error: Invalid JSON format in {file_path}: {e}")
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
    
    page_width, _ = doc.pagesize
    max_per_row = 12 if not secondary_instrument else 6
    footer_height = 100
    

    # Instrument-specific adjustments
    #min_chord_spacing = 10 if instrument == "ukulele" else 70

    
    def prepare_chords(chords):
        diagrams = []
        for chord in chords:
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


    max_chords_per_row = 12 if not secondary_instrument else 6  # 6 per instrument if two

    primary_diagrams = prepare_chords([chord for chord in relevant_chords if chord.get("instrument") == instrument])
    secondary_diagrams = prepare_chords([chord for chord in relevant_chords if secondary_instrument and chord.get("instrument") == secondary_instrument])

    if secondary_instrument:
        primary_rows = (len(primary_diagrams) + max_chords_per_row - 1) // max_chords_per_row  # Per instrument
        secondary_rows = (len(secondary_diagrams) + max_chords_per_row - 1) // max_chords_per_row  # Per instrument
        rows_needed = max(primary_rows, secondary_rows)  # Take the max since they stack
    else:
        rows_needed = (len(primary_diagrams) + max_chords_per_row - 1) // max_chords_per_row  # Full page

    #print(f"DEBUG: Number of chords={len(primary_diagrams)}, max_chords_per_row={max_chords_per_row}, rows_needed={rows_needed}")



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
