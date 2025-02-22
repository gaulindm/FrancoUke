from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph,Flowable, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.platypus.flowables import Flowable
import json
import os
import re
from .chord_utils import load_chords, extract_used_chords, draw_footer, ChordDiagram
from songbook.models import SongFormatting  # Use absolute import

from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from songbook.utils.transposer import transpose_chord, normalize_chord  # ✅ Import normalize_chord
from songbook.utils.transposer import transpose_chord  # ✅ Make sure this path is correct!


def draw_footer_with_doc(canvas, doc):
        """
        Wrapper function to call draw_footer with required arguments.
        """
        draw_footer(
            canvas, doc, doc.relevant_chords, doc.chord_spacing, doc.row_spacing, doc.is_lefty,
            instrument=doc.instrument,
            secondary_instrument=doc.secondary_instrument,
            is_printing_alternate_chord=doc.is_printing_alternate_chord,
            acknowledgement=doc.acknowledgement
        )

def generate_songs_pdf(response, songs, user, transpose_value=0, formatting=None):
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=2, bottomMargin=80, leftMargin=20, rightMargin=20)
    styles = getSampleStyleSheet()
    base_style = styles["BodyText"]
    elements = []

    instrument = user.userpreference.primary_instrument
    
    # ✅ Retrieve user instrument preferences first
    user_preferences = getattr(user, "userpreference", None)
    if not user_preferences:
        raise ValueError("User preferences not found")

    primary_instrument = user_preferences.primary_instrument
    secondary_instrument = getattr(user_preferences, "secondary_instrument", None)

    is_lefty = user.userpreference.is_lefty
    is_printing_alternate_chord = user.userpreference.is_printing_alternate_chord

    # ✅ Ensure primary_instrument is set
    if not primary_instrument:
        raise ValueError("Primary instrument not found in user preferences")

    # ✅ Now it's safe to load chords
    chords_primary = load_chords(primary_instrument)
    chords_secondary = load_chords(secondary_instrument) if secondary_instrument else []



    # Tag chords with their instrument for identification in draw_footer
    for chord in chords_primary:
        chord["instrument"] = primary_instrument  
    for chord in chords_secondary:
        chord["instrument"] = secondary_instrument  

    # Merge chord lists
    chords = chords_primary + chords_secondary




    used_chords = [normalize_chord(chord) for chord in extract_used_chords(songs[0].lyrics_with_chords)]
    






    
    # ✅ Transpose chords before extracting relevant diagrams
    if not hasattr(response, "transposed_chords"):
        response.transposed_chords = {transpose_chord(chord, transpose_value) for chord in used_chords}
    
    transposed_chords = response.transposed_chords  # ✅ Ensure it's always defined
    

    relevant_chords = [chord for chord in chords if chord["name"].lower() in map(str.lower, transposed_chords)]


   # Store relevant data in doc for later use in draw_footer
    doc.relevant_chords = relevant_chords
    doc.instrument = primary_instrument
    doc.secondary_instrument = secondary_instrument
    doc.chord_spacing = 50 if primary_instrument == "ukulele" else 70
    doc.row_spacing = 72
    doc.is_lefty = is_lefty
    doc.is_printing_alternate_chord = is_printing_alternate_chord
    doc.acknowledgement = songs[0].acknowledgement if hasattr(songs[0], 'acknowledgement') else ""








    # Get user formatting settings or create defaults
    formatting, _ = SongFormatting.objects.get_or_create(user=user, song=songs[0])

    diagrams_to_draw = []
    for chord in relevant_chords:
        diagrams_to_draw.append({
            "name": chord["name"],
            "variation": chord["variations"][0]
        })
        if is_printing_alternate_chord and len(chord["variations"]) > 1:
            diagrams_to_draw.append({
                "name": chord["name"],
                "variation": chord["variations"][1]
            })

    # Adjust chord spacing and layout
    chord_spacing = 20 if instrument == "ukulele" else 70  
    page_width, page_height = letter

    # Correctly determine max_chords_per_row
    max_chords_per_row = 12 if not secondary_instrument else 6  # 6 per instrument if secondary is present

    # Separate chord counts for primary & secondary instruments
    primary_diagrams = len([chord for chord in relevant_chords if chord.get("instrument") == instrument])
    secondary_diagrams = len([chord for chord in relevant_chords if secondary_instrument and chord.get("instrument") == secondary_instrument])

    # Include 2 variations if < 7 chords
    total_primary = primary_diagrams * (2 if primary_diagrams < 7 else 1)
    total_secondary = secondary_diagrams * (2 if secondary_diagrams < 7 else 1)

    # Calculate rows per instrument
    primary_rows = (total_primary + max_chords_per_row - 1) // max_chords_per_row
    secondary_rows = (total_secondary + max_chords_per_row - 1) // max_chords_per_row

    # Take max of both since they stack
    rows_needed = max(primary_rows, secondary_rows)

    row_spacing = 72  # Space between rows
    diagram_height = rows_needed * row_spacing

    # Adjust bottom margin dynamically
    doc.bottomMargin = max(80, diagram_height + 20)

    # Debugging output
    print(f"Primary diagrams: {total_primary}, Secondary diagrams: {total_secondary}, Max chords per row: {max_chords_per_row}, Rows needed: {rows_needed}, Bottom margin: {doc.bottomMargin}")


    songwriter_style = ParagraphStyle(
        'SongwriterStyle',
        parent=styles['Normal'],  # Inherit other properties from the Normal style
        alignment=1,  # Center alignment
        fontSize=14,  # Adjust size if needed
        spaceBefore=6,
        spaceAfter=6
    )

    recording_style = ParagraphStyle(
        'RecordingStyle',
        parent=styles['Normal'],  # Inherit other properties from the Normal style
        alignment=1,  # Center alignment
        fontSize=13,  # Adjust size if needed
        spaceBefore=6,
        spaceAfter=6
    )

    first_vocal_note_style = ParagraphStyle(
        'FirstVocalNoteStyle',
        parent=styles['Normal'],  # Inherit from the Normal style
        alignment=2,  # Right-aligned text
        fontSize=12,  # Optional: Adjust the font size
        spaceBefore=6,  # Optional: Add space above the paragraph
        spaceAfter=6,  # Optional: Add space below the paragraph
    )

    def get_style(section):
        config = getattr(formatting, section, {})  # Get JSON formatting for section

        # Get the default "BodyText" style from ReportLab
        base_style = styles["BodyText"]

        return ParagraphStyle(
            name=section,
            parent=base_style,  # Use base style as the parent
            fontSize=config.get("font_size", 13),
            textColor=config.get("font_color", "#000000"),
            fontName=config.get("font_family", "Helvetica") 
                if config.get("font_family", "Helvetica") in ["Helvetica", "Times-Roman", "Courier"] 
                else "Helvetica",
            leading=config.get("line_spacing", 1.2) * config.get("font_size", 13),
            #spaceBefore=config.get("spacing_before", 24),
            #spaceAfter=config.get("spacing_after", 24),
            alignment={
                "left": TA_LEFT,
                "center": TA_CENTER,
                "right": TA_RIGHT
            }.get(config.get("alignment", "left"), TA_LEFT)
        )



    # Apply user-defined styles (fallback to defaults)
    intro_style = get_style("intro")
    verse_style = get_style("verse")
    chorus_style = get_style("chorus")
    bridge_style = get_style("bridge")
    interlude_style = get_style("interlude")
    outro_style = get_style("outro")


    for song in songs:
            # Header Section
        metadata = song.metadata or {}
        artist = metadata.get('artist', 'Unknown Artist')
        album = metadata.get('album', 'Unknown')
        songwriter = metadata.get('songwriter', 'Unknown')
        year = metadata.get('year', 'Unknown')
        recording = metadata.get('recording', 'Unknown')

        recorded_by_text = f"{metadata.get('recording', 'Unknown')} recording by {metadata.get('artist', 'Unknown Artist')}"
        #if metadata.get('album', ''):
        #    recorded_by_text += f" on {metadata['album']}"
        if metadata.get('year', ''):
            recorded_by_text += f" in {metadata['year']}"

        header_data = [
            [
                Paragraph(f"{metadata.get('timeSignature', '')}", styles['Normal']),
                Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", styles['Title']),
                Paragraph(f"First Vocal Note: {metadata.get('1stnote', 'N/A')}", first_vocal_note_style),
            ],
            [Paragraph(f"{metadata.get('songwriter', '')}", songwriter_style),  "","",],
            [Paragraph(recorded_by_text, recording_style), "","",],
        ]

        header_table = Table(header_data, colWidths=[120, 360, 120])
        header_table.setStyle(TableStyle([
            ('SPAN', (0, 1), (2, 1)),  # Merge all three cells in the second row
            ('SPAN', (0, 2), (2, 2)),  # Merge all three cells in the third row
            
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells as a base
            ('VALIGN', (1, 1), (1, 1), 'MIDDLE'),  # Specifically center align the songwriter cell
            ('LEFTPADDING', (1, 1), (1, 1), 10),
            ('RIGHTPADDING', (1, 1), (1, 1), 10),
            ('TOPPADDING', (1, 1), (2, 2), 0),
            ('BOTTOMPADDING', (1, 1), (1, 1), 5),
            #('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for debugging
        ]))
        elements.append(header_table)
        #elements.append(Spacer(1, 12))

      # Lyrics Section with section handling
        lyrics_with_chords = song.lyrics_with_chords or []


        # Initialize necessary variables
        section_type = None  # Tracks active section (Chorus, Intro, Bridge, Outro)
        section_buffer = []  # Stores lyrics inside structured sections
        section_table_data = []  # Stores formatted section content
        paragraph_buffer = []  # Stores unstructured verses (normal lyrics)

        for group in lyrics_with_chords:
            for item in group:
                if "directive" in item:
                    # Detect the start of a structured section
                    if item["directive"] in ["{soc}", "{soi}", "{sob}", "{soo}", "{sod}"]:
                        # Store any buffered verse before switching sections
                        if paragraph_buffer:
                            elements.append(Paragraph(" ".join(paragraph_buffer), verse_style))
                            #elements.append(Spacer(1, 12))
                            paragraph_buffer = []

                        # Set section type
                        section_type = {
                            "{soc}": "Chorus",
                            "{soi}": "Intro",
                            "{sob}": "Bridge",
                            "{soo}": "Outro",
                            "{sod}": "Interlude"
                        }[item["directive"]]

                        section_table_data = []
                        section_buffer = []
                        continue

                    # Detect the end of a structured section
                    elif item["directive"] in ["{eoc}", "{eoi}", "{eob}", "{eoo}", "{eod}"]:
                        if section_type and section_buffer:
                            section_table_data.append([
                                "", 
                                Paragraph(" ".join(section_buffer), 
                                    chorus_style if section_type == "Chorus" 
                                    else intro_style if section_type == "Intro" 
                                    else bridge_style if section_type == "Bridge" 
                                    else outro_style if section_type == "Outro"
                                    else interlude_style)  # New Interlude Formatting
                            ])

                        # Determine which style applies to the section
                        style = (
                            chorus_style if section_type == "Chorus"
                            else intro_style if section_type == "Intro"
                            else bridge_style if section_type == "Bridge"
                            else outro_style if section_type == "Outro"
                            else interlude_style
                        )

                        # Extract spacing values from the style
                        spacing_before = style.spaceBefore
                        spacing_after = style.spaceAfter

                        if section_type and section_table_data:
                            # Retrieve user-defined formatting from Django model
                            section_format = getattr(formatting, section_type.lower(), {})  # Example: formatting.chorus
                            spacing_before = section_format.get("spacing_before", 12)
                            spacing_after = section_format.get("spacing_after", 12)

                            # Insert section name at (0,0)
                            section_table_data.insert(0, [
                                Paragraph(f"<b>{section_type}:</b>", base_style), 
                                section_table_data.pop(0)[1]
                            ])

                            section_table = Table(section_table_data, colWidths=[80, 440], hAlign='LEFT')
                            section_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('TOPPADDING', (0, 0), (-1, 0), spacing_before),  # Simulates spaceBefore
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Simulates line spacing within table
                                ('BOTTOMPADDING', (0, -1), (-1, -1), spacing_after),  # Simulates spaceAfter
                            ]))
                            elements.append(section_table)
                            #elements.append(Spacer(1, 12))

                        # Reset section tracking
                        section_type = None
                        section_buffer = []
                        continue

                elif "format" in item:
                    if item["format"] == "LINEBREAK":
                        if section_type and section_buffer:
                            full_line = " ".join(section_buffer)
                            section_table_data.append(["", Paragraph(full_line, 
                                chorus_style if section_type == "Chorus" 
                                else intro_style if section_type == "Intro" 
                                else bridge_style if section_type == "Bridge" 
                                else outro_style)])
                            section_buffer = []   

                        elif not section_type and paragraph_buffer:
                            paragraph_buffer.append("<br/>")  # Keep verse formatting

                    elif item["format"] == "PARAGRAPHBREAK":
                        if paragraph_buffer:
                            paragraph_text = " ".join(paragraph_buffer)
                            style = verse_style  # Verses always use verse_style
                            elements.append(Paragraph(paragraph_text, style))
                            elements.append(Spacer(1, 48))
                            paragraph_buffer = []

                elif "lyric" in item:
                    chord = item.get("chord", "")
                    
                    # ✅ Ensure transposition happens ONCE
                    if chord and "transposed" not in item:
                        item["chord"] = chord
                        item["transposed"] = True  # ✅ Mark it as transposed to avoid duplicate transposition

                    lyric = item["lyric"]
                    line = f"<b>[{item['chord']}]</b> {lyric}" if item["chord"] else lyric

                    if section_type:
                        section_buffer.append(line)  # Store for structured sections
                    else:
                        paragraph_buffer.append(line)  # Store for normal verses

        # Ensure any remaining structured section is processed
        if section_type and section_buffer:
            section_table_data.append([
                "", 
                Paragraph(" ".join(section_buffer), 
                    chorus_style if section_type == "Chorus" 
                    else intro_style if section_type == "Intro" 
                    else bridge_style if section_type == "Bridge" 
                    else outro_style)
            ])

        if section_type and section_table_data:
            section_table_data.insert(0, [
                Paragraph(f"<b>{section_type}:</b>", base_style), 
                section_table_data.pop(0)[1]
            ])

            section_table = Table(section_table_data, colWidths=[80, 440], hAlign='CENTER')
            section_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(section_table)
            #elements.append(Spacer(1, 24))

        # Ensure any remaining verse is added as a paragraph
        if paragraph_buffer:
            elements.append(Paragraph(" ".join(paragraph_buffer), verse_style))
            #elements.append(Spacer(1, 24))
            paragraph_buffer = []



        elements.append(PageBreak())  # Separate songs by page

    # Define spacing and build the document
    page_width, page_height = letter
    available_width = page_width - 2 * doc.leftMargin
    max_chords_per_row = 8
    chord_spacing = available_width / max_chords_per_row
    row_spacing = 72


      # Build PDF with custom footer handling
    doc.build(
        elements,
        onFirstPage=lambda c, d: draw_footer_with_doc(c, d),
        onLaterPages=lambda c, d: draw_footer_with_doc(c, d)
    )

    