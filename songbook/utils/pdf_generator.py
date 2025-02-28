from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Flowable, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from .chord_utils import load_chords, extract_used_chords, draw_footer, ChordDiagram
from songbook.models import SongFormatting
from songbook.utils.transposer import transpose_chord, normalize_chord
import json
import os
import re


def draw_footer_with_doc(canvas, doc):
    draw_footer(
        canvas, doc, doc.relevant_chords, doc.chord_spacing, doc.row_spacing, doc.is_lefty,
        instrument=doc.instrument,
        secondary_instrument=doc.secondary_instrument,
        is_printing_alternate_chord=doc.is_printing_alternate_chord,
        acknowledgement=doc.acknowledgement
    )


def get_user_preferences(user):
    user_preferences = getattr(user, "userpreference", None)
    if not user_preferences:
        raise ValueError("User preferences not found")
    
    primary_instrument = user_preferences.primary_instrument
    if not primary_instrument:
        raise ValueError("Primary instrument not found in user preferences")
    
    return {
        "primary_instrument": primary_instrument,
        "secondary_instrument": getattr(user_preferences, "secondary_instrument", None),
        "is_lefty": user_preferences.is_lefty,
        "is_printing_alternate_chord": user_preferences.is_printing_alternate_chord
    }


def load_relevant_chords(songs, user_prefs, transpose_value):
    chords_primary = load_chords(user_prefs["primary_instrument"])
    chords_secondary = load_chords(user_prefs["secondary_instrument"]) if user_prefs["secondary_instrument"] else []

    for chord in chords_primary:
        chord["instrument"] = user_prefs["primary_instrument"]
    for chord in chords_secondary:
        chord["instrument"] = user_prefs["secondary_instrument"]

    all_chords = chords_primary + chords_secondary
    used_chords = [normalize_chord(chord) for chord in extract_used_chords(songs[0].lyrics_with_chords)]
    transposed_chords = {transpose_chord(chord, transpose_value) for chord in used_chords}

    return [chord for chord in all_chords if chord["name"].lower() in map(str.lower, transposed_chords)]


def get_paragraph_styles(formatting):
    styles = getSampleStyleSheet()
    base_style = styles["BodyText"]

    def create_style(section):
        config = getattr(formatting, section, {})
        return ParagraphStyle(
            name=section,
            parent=base_style,
            fontSize=config.get("font_size", 13),
            textColor=config.get("font_color", "#000000"),
            fontName=config.get("font_family", "Helvetica") if config.get("font_family", "Helvetica") in ["Helvetica", "Times-Roman", "Courier"] else "Helvetica",
            leading=config.get("line_spacing", 1.2) * config.get("font_size", 13),
            spaceBefore=config.get("spacing_before", 12),
            spaceAfter=config.get("spacing_after", 12),
            alignment={"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}.get(config.get("alignment", "left"), TA_LEFT)
        )

    return {
        "intro": create_style("intro"),
        "verse": create_style("verse"),
        "chorus": create_style("chorus"),
        "bridge": create_style("bridge"),
        "interlude": create_style("interlude"),
        "outro": create_style("outro")
    }


def generate_songs_pdf(response, songs, user, transpose_value=0, formatting=None):
    # Calculate diagram rows for bottom margin adjustment
    def calculate_diagram_rows(chords, max_chords_per_row=8):
        return (len(chords) + max_chords_per_row - 1) // max_chords_per_row
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=2, bottomMargin=80, leftMargin=20, rightMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    user_prefs = get_user_preferences(user)
    relevant_chords = load_relevant_chords(songs, user_prefs, transpose_value)

    doc.relevant_chords = relevant_chords
    doc.instrument = user_prefs["primary_instrument"]
    doc.secondary_instrument = user_prefs["secondary_instrument"]
    doc.chord_spacing = 50 if user_prefs["primary_instrument"] == "ukulele" else 70
    doc.row_spacing = 72
    doc.is_lefty = user_prefs["is_lefty"]
    doc.is_printing_alternate_chord = user_prefs["is_printing_alternate_chord"]
    doc.acknowledgement = songs[0].acknowledgement if hasattr(songs[0], 'acknowledgement') else ""

    # Adjust bottom margin based on chord diagrams
    diagram_rows = calculate_diagram_rows(relevant_chords)
    diagram_height = diagram_rows * doc.row_spacing
    doc.bottomMargin = max(80, diagram_height + 20)

    formatting = formatting or SongFormatting.objects.filter(user=user, song=songs[0]).first()
    if not formatting:
        formatting = SongFormatting.objects.filter(user__username="Gaulind", song=songs[0]).first()

    styles_dict = get_paragraph_styles(formatting)

    for song in songs:
        elements.extend(build_song_elements(song, styles, styles_dict))
        elements.append(PageBreak())

    doc.build(
        elements,
        onFirstPage=lambda c, d: draw_footer_with_doc(c, d),
        onLaterPages=lambda c, d: draw_footer_with_doc(c, d)
    )


def build_song_elements(song, styles, styles_dict):
    elements = []
    metadata = song.metadata or {}

    songwriter_style = ParagraphStyle(
        'SongwriterStyle',
        parent=styles['Normal'],  # Inherit other properties from the Normal style
        alignment=1,  # Center alignment
        fontSize=14,  # Adjust size if needed
        spaceBefore=2,
        spaceAfter=2
    )

    keymatch_style = ParagraphStyle(
        'keymatchStyle',
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

    recorded_by_text = f"{metadata.get('keymatch', 'Unknown')} au clip par {metadata.get('artist', 'Unknown Artist')}"
        #if metadata.get('album', ''):
        #    recorded_by_text += f" on {metadata['album']}"
    if metadata.get('year', ''):
        recorded_by_text += f" en {metadata['year']}"

    header_data = [
        [
            Paragraph(f"{metadata.get('timeSignature', '')}", styles['Normal']),
            Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", styles['Title']),
            Paragraph(f"1e note vocale: {metadata['1stnote']}", first_vocal_note_style) if metadata.get('1stnote') else Paragraph("", first_vocal_note_style),
        ],
        [Paragraph(f"{metadata.get('songwriter', '')}", songwriter_style), "", "",],
        [Paragraph(recorded_by_text, keymatch_style), "", "",],
    ]

    header_table = Table(header_data, colWidths=[110, 380, 110])
    header_table.setStyle(TableStyle([
            ('SPAN', (0, 1), (2, 1)),  # Merge all three cells in the second row
            ('SPAN', (0, 2), (2, 2)),  # Merge all three cells in the third row
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells as a base
            ('VALIGN', (1, 1), (1, 1), 'MIDDLE'),  # Specifically center align the songwriter cell
            ('LEFTPADDING', (1, 1), (1, 1),0),
            ('RIGHTPADDING', (1, 1), (1, 1), 0),
            ('TOPPADDING', (1, 1), (2, 2), 0),
            ('BOTTOMPADDING', (1, 0), (1, 0), 0),
            ('TOPPADDING', (1, 1), (1, 1), 0),
            ('BOTTOMPADDING', (1, 1), (1, 2), 1),
            #('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for debugging
    ]))
    elements.append(header_table)

    lyrics_elements = build_lyrics_elements(song.lyrics_with_chords, styles_dict, styles['BodyText'])
    elements.extend(lyrics_elements)

    return elements


def build_lyrics_elements(lyrics_with_chords, styles_dict, base_style):
    elements = []
    paragraph_buffer = []
    section_type = None

    directive_map = {
        "{soi}": "Intro",
        "{soc}": "Chorus",
        "{sov}": "Verse",
        "{sob}": "Bridge",
        "{soo}": "Outro",
        "{sod}": "Interlude",
        "{eoi}": None,
        "{eoc}": None,
        "{eov}": None,
        "{eob}": None,
        "{eoo}": None,
        "{eod}": None
    }

    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                directive = item["directive"].lower()
                if directive in directive_map:
                    if paragraph_buffer:
                        paragraph_text = " ".join(paragraph_buffer)
                        style = styles_dict.get(section_type.lower(), styles_dict["verse"]) if section_type else styles_dict["verse"]
                        if section_type and section_type.lower() != "verse":
                            # Non-verse sections in a table with section name
                            
                            section_labels = {"chorus": "Refrain", "verse": "Couplet        ", "bridge": "Pont", "outro": "Outro"}
                            display_name = section_labels.get(section_type.lower(), section_type)  # Default to section_type if not mapped

                            section_table = Table([
                                [Paragraph(f"<b>{display_name}:</b>", base_style), Paragraph(paragraph_text, style)]
                            ], colWidths=[60, 460], hAlign='LEFT')



                            section_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                #('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for debugging
                                #('BOX', (0, 0), (-1, -1), 0.5, colors.grey)
                            ]))
                            elements.append(section_table)
                        else:
                            # Verses as simple paragraphs
                            elements.append(Paragraph(paragraph_text, style))
                        paragraph_buffer = []
                    section_type = directive_map[directive]
                    continue
            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]
                line = f"<b>[{chord}]</b> {lyric}" if chord else lyric
                paragraph_buffer.append(line)
            elif "format" in item and item["format"] == "LINEBREAK":
                paragraph_buffer.append("<br/>")

    if paragraph_buffer:
        paragraph_text = " ".join(paragraph_buffer)
        style = styles_dict.get(section_type.lower(), styles_dict["verse"]) if section_type else styles_dict["verse"]
        if section_type and section_type.lower() != "verse":
            section_table = Table([
                [Paragraph(f"<b>{section_type}:</b>", base_style), Paragraph(paragraph_text, style)]
            ], colWidths=[70, 450], hAlign='LEFT')
            section_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(section_table)
        else:
            elements.append(Paragraph(paragraph_text, style))

    return elements
