#pdf_generator.py
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


# songbook/utils/pdf_generator.py
from users.models import UserPreference

def get_user_preferences(user):
    """
    Return user preferences if available, otherwise sensible defaults.
    Falls back safely for anonymous users.
    """
    default_prefs = {
        "primary_instrument": "ukulele",
        "secondary_instrument": None,
        "is_left_handed": False,
        "show_alternate_chords": False,
    }

    if not user or not user.is_authenticated:
        return default_prefs

    try:
        prefs, _ = UserPreference.objects.get_or_create(
            user=user,
            defaults=default_prefs,
        )
        return {
            "primary_instrument": prefs.primary_instrument,
            "secondary_instrument": getattr(prefs, "secondary_instrument", None),
            "is_left_handed": getattr(prefs, "is_left_handed", False),
            "show_alternate_chords": getattr(prefs, "show_alternate_chords", False),
        }
    except Exception:
        return default_prefs

import re

def chord_equivalent(a: str, b: str) -> bool:
    """
    Smart chord name comparison (FrancoUke-safe):
    - Treats CM7 == Cmaj7 == CMAJ7
    - Keeps Cm7 (minor) distinct from CM7 (major)
    - Ignores strumming slashes (Em/// == Em)
    - Case-insensitive for maj-variants only
    """
    import re

    if not a or not b:
        return False

    a = a.strip()
    b = b.strip()

    # 🧹 Remove trailing slashes (Em/// → Em)
    a = re.sub(r'/+$', '', a)
    b = re.sub(r'/+$', '', b)

    # 🧹 Remove alternate bass chords (D/F# → D)
    a = re.sub(r'/[A-G][#b]?$', '', a)
    b = re.sub(r'/[A-G][#b]?$', '', b)

    # 🧠 If either chord explicitly uses "m" and not "maj" → it's a minor chord → exact match only
    if re.match(r'^[A-G][#b]?m(?!aj)', a):
        return a == b

    # 🧠 Normalize "maj" variants: CM7, Cmaj7, CΔ7 → all become CM7
    def normalize_maj(name):
        name = re.sub(r'(?i)maj', 'M', name)
        name = re.sub(r'(?i)Δ', 'M', name)
        return name

    a_norm = normalize_maj(a).lower()
    b_norm = normalize_maj(b).lower()

    return a_norm == b_norm


# Put this helper near the top of your file (you already import `re`).
def apply_color_markup(text):
    """
    Convert simple custom tags into reportlab-compatible <font color="..."> tags.
    Supports: <red>...</red>, <blue>...</blue>, <highlight color="...">...</highlight>
    and short tags <r>...</r>, <g>...</g>, etc.
    """
    color_map = {
        'red': 'red',
        'blue': 'blue',
        'green': 'green',
        'yellow': 'gold',
        'orange': 'orange',
        'pink': 'hotpink',
        'purple': 'purple',
    }

    # Named color tags like <red>...</red>
    for tag, color in color_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<font color='{color}'>{m.group(1)}</font>", text)

    # <highlight color="...">...</highlight>
    pattern = re.compile(r'<highlight\s+color="(.*?)">(.*?)</highlight>', re.IGNORECASE | re.DOTALL)
    text = pattern.sub(lambda m: f"<font color='{m.group(1)}'>{m.group(2)}</font>", text)

    # Short tags like <r>...</r> (r=red, g=green, b=blue, y=yellow/gold)
    short_map = {'r': 'red', 'g': 'green', 'blue': 'blue', 'y': 'gold'}
    for tag, color in short_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<font color='{color}'>{m.group(1)}</font>", text)

    return text


def build_lyrics_elements(lyrics_with_chords, styles_dict, base_style, site_name):
    elements = []
    paragraph_buffer = []
    section_type = None

    # Directive map (same as your code)
    directive_map = {
        "FrancoUke": {
            "{soi}": "Intro",
            "{soc}": "Refrain",
            "{sov}": "Couplet",
            "{sob}": "Pont",
            "{soo}": "Outro",
            "{sod}": "Interlude",
            "{eoi}": None,
            "{eoc}": None,
            "{eov}": None,
            "{eob}": None,
            "{eoo}": None,
            "{eod}": None
        },
        "StrumSphere": {
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
    }

    selected_directive_map = directive_map.get(site_name, directive_map["StrumSphere"])

    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                directive = item["directive"].lower()
                if directive in selected_directive_map:
                    # flush existing paragraph buffer
                    if paragraph_buffer:
                        paragraph_text = "".join(paragraph_buffer)
                        paragraph_text = apply_color_markup(paragraph_text)  # apply color tags
                        style = styles_dict.get(section_type.lower(), styles_dict["verse"]) if section_type else styles_dict["verse"]

                        if section_type and section_type.lower() != "verse":
                            # Non-verse sections in a table with section name
                            section_table = Table([
                                [Paragraph(f"<b>{section_type}:</b>", base_style), Paragraph(paragraph_text, style)]
                            ], colWidths=[60, 460], hAlign='LEFT')
                            section_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ]))
                            elements.append(section_table)
                        else:
                            # Verses as simple paragraphs
                            elements.append(Paragraph(paragraph_text, style))

                        paragraph_buffer = []

                    # update current section type and continue
                    section_type = selected_directive_map[directive]
                    continue

            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]

                # build the line with chord markup as before
                if chord:
                    if lyric.startswith("-"):
                        # Chord is inside a hyphenated word — no space before
                        line = f"<b>[{chord}]</b>{lyric}"
                    elif lyric[:1].isalpha():
                        if paragraph_buffer and paragraph_buffer[-1].endswith("-"):
                            # No space before chord if previous content ends in hyphen
                            line = f"<b>[{chord}]</b>{lyric}"
                        else:
                            # Otherwise, it's a new word — space before chord
                            line = f" <b>[{chord}]</b>{lyric}"
                    else:
                        # Default case — no space
                        line = f"<b>[{chord}]</b>{lyric}"
                else:
                    line = lyric

                paragraph_buffer.append(line)

            elif "format" in item and item["format"] == "LINEBREAK":
                paragraph_buffer.append("<br/>")

    # flush any remaining buffer after loop
    if paragraph_buffer:
        paragraph_text = "".join(paragraph_buffer)
        paragraph_text = apply_color_markup(paragraph_text)  # apply color tags
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


def load_relevant_chords(songs, user_prefs, transpose_value):
    chords_primary = load_chords(user_prefs["primary_instrument"])
    chords_secondary = load_chords(user_prefs["secondary_instrument"]) if user_prefs["secondary_instrument"] else []

    for chord in chords_primary:
        chord["instrument"] = user_prefs["primary_instrument"]
    for chord in chords_secondary:
        chord["instrument"] = user_prefs["secondary_instrument"]

    all_chords = chords_primary + chords_secondary
    used_chords = [normalize_chord(chord).strip() for chord in extract_used_chords(songs[0].lyrics_with_chords)]
    transposed_chords = {transpose_chord(chord.strip(), transpose_value).strip() for chord in used_chords}

    return [
        chord for chord in all_chords
        if any(chord_equivalent(chord["name"], t) for t in transposed_chords)
    ]


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


def generate_songs_pdf(response, songs, user, transpose_value=0, formatting=None, site_name="FrancoUke"):
    print(f"DEBUG: site_name received → {site_name}")  # ✅ Check if site_name is correct

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
    doc.chord_spacing = 45 if user_prefs["primary_instrument"] == "ukulele" else 60
    doc.row_spacing = 70
    doc.is_lefty = user_prefs["is_left_handed"]
    doc.is_printing_alternate_chord = user_prefs["show_alternate_chords"]
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
        elements.extend(build_song_elements(song, styles, styles_dict, site_name))  # ✅ Pass site_name correctly
        elements.append(PageBreak())

    doc.build(
        elements,
        onFirstPage=lambda c, d: draw_footer_with_doc(c, d),
        onLaterPages=lambda c, d: draw_footer_with_doc(c, d)
    )


def build_song_elements(song, styles, styles_dict,site_name):
    elements = []
    metadata = song.metadata or {}

    print(f"DEBUG: site_name inside build_song_elements → {site_name}")


    songwriter_style = ParagraphStyle(
        'SongwriterStyle',
        parent=styles['Normal'],  # Inherit other properties from the Normal style
        alignment=1,  # Center alignment
        fontSize=14,  # Adjust size if needed
        spaceBefore=2,
        spaceAfter=2
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
        #alignment=2,  # Right-aligned text
        fontSize=12,  # Optional: Adjust the font size
        spaceBefore=6,  # Optional: Add space above the paragraph
        spaceAfter=6,  # Optional: Add space below the paragraph
    )

    capo_value = metadata.get('capo')

    # Convert capo_value to an integer if possible, or check for "Based"
    if isinstance(capo_value, str) and capo_value.lower() == "based":
        capo_text = "Based on clip"
    else:
        try:
            capo_value = int(capo_value)
        except (TypeError, ValueError):
            capo_value = 0

        if site_name == "FrancoUke":
            capo_text = f"Capo ({capo_value}) pour correspondre" if capo_value > 0 else "Correspond"
        else:
            capo_text = f"Capo ({capo_value}) to match" if capo_value > 0 else "Matches recording"


    #recorded_by_text = f"{capo_text} au clip par {metadata.get('artist', 'Unknown Artist')}"
    if site_name == "FrancoUke":
        recorded_by_text = f"{capo_text} au clip par {metadata.get('artist', 'Artiste Inconnu')}"
    else:
        recorded_by_text = f"{capo_text} in the recording by {metadata.get('artist', 'Unknown Artist')}"


    if metadata.get('year', ''):
        if site_name == "FrancoUke":
            recorded_by_text += f" en {metadata['year']}"
        else:
            recorded_by_text += f" in {metadata['year']}"


    def contains_slash_chord(lyrics_with_chords):
        """ Checks if any chord in the song contains a '/' """
        used_chords = extract_used_chords(lyrics_with_chords)
        return any('/' in chord for chord in used_chords)

    # Check if the song contains a slash chord
    has_slash_chord = contains_slash_chord(song.lyrics_with_chords)

    def format_chord_display(chord_name):
        """ Returns the chord name if it contains '/', otherwise returns an empty string. """
        return chord_name if '/' in chord_name else ""

    header_data = [
        [
            Paragraph(metadata.get('timeSignature', '') if metadata.get('timeSignature') else "", styles['Normal']),
            Paragraph(f"<b>{song.songTitle or ('Chanson sans titre' if site_name == 'FrancoUke' else 'Untitled Song')}</b>", styles['Title']),
            Paragraph("(/=one strum)", styles['Normal']) if has_slash_chord else Paragraph("", styles['Normal']),  # Only show if needed
        ],
        [
            Paragraph(
                f"{'1e note vocale' if site_name == 'FrancoUke' else 'First vocal note'}: {metadata['1stnote']}",
                first_vocal_note_style
            ) if metadata.get('1stnote') else Paragraph("", first_vocal_note_style),
            Paragraph(f"{metadata.get('songwriter', '')}", songwriter_style), "",
        ],
        [
            Paragraph(recorded_by_text, recording_style),
            Paragraph(format_chord_display(metadata.get('chord', ''))),  # Show chord only if it has '/'
            "",
        ],
    ]




    header_table = Table(header_data, colWidths=[110, 380, 110])
    header_table.setStyle(TableStyle([
            #('SPAN', (0, 1), (2, 1)),  # Merge all three cells in the second row
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
    lyrics_elements = build_lyrics_elements(song.lyrics_with_chords, styles_dict, styles['BodyText'], site_name)

    #    lyrics_elements = build_lyrics_elements(song.lyrics_with_chords, styles_dict, styles['BodyText'])
    elements.extend(lyrics_elements)

    return elements

def build_lyrics_elements(lyrics_with_chords, styles_dict, base_style, site_name):
    elements = []
    paragraph_buffer = []
    section_type = None

    # Directive map (same as your code)
    directive_map = {
        "FrancoUke": {
            "{soi}": "Intro",
            "{soc}": "Refrain",
            "{sov}": "Couplet",
            "{sob}": "Pont",
            "{soo}": "Outro",
            "{sod}": "Interlude",
            "{eoi}": None,
            "{eoc}": None,
            "{eov}": None,
            "{eob}": None,
            "{eoo}": None,
            "{eod}": None
        },
        "StrumSphere": {
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
    }

    selected_directive_map = directive_map.get(site_name, directive_map["StrumSphere"])

    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                directive = item["directive"].lower()
                if directive in selected_directive_map:
                    # flush existing paragraph buffer
                    if paragraph_buffer:
                        paragraph_text = "".join(paragraph_buffer)
                        paragraph_text = apply_color_markup(paragraph_text)  # apply color tags
                        style = styles_dict.get(section_type.lower(), styles_dict["verse"]) if section_type else styles_dict["verse"]

                        if section_type and section_type.lower() != "verse":
                            # Non-verse sections in a table with section name
                            section_table = Table([
                                [Paragraph(f"<b>{section_type}:</b>", base_style), Paragraph(paragraph_text, style)]
                            ], colWidths=[60, 460], hAlign='LEFT')
                            section_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ]))
                            elements.append(section_table)
                        else:
                            # Verses as simple paragraphs
                            elements.append(Paragraph(paragraph_text, style))

                        paragraph_buffer = []

                    # update current section type and continue
                    section_type = selected_directive_map[directive]
                    continue

            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]

                # build the line with chord markup as before
                if chord:
                    if lyric.startswith("-"):
                        # Chord is inside a hyphenated word — no space before
                        line = f"<b>[{chord}]</b>{lyric}"
                    elif lyric[:1].isalpha():
                        if paragraph_buffer and paragraph_buffer[-1].endswith("-"):
                            # No space before chord if previous content ends in hyphen
                            line = f"<b>[{chord}]</b>{lyric}"
                        else:
                            # Otherwise, it's a new word — space before chord
                            line = f" <b>[{chord}]</b>{lyric}"
                    else:
                        # Default case — no space
                        line = f"<b>[{chord}]</b>{lyric}"
                else:
                    line = lyric

                paragraph_buffer.append(line)

            elif "format" in item and item["format"] == "LINEBREAK":
                paragraph_buffer.append("<br/>")

    # flush any remaining buffer after loop
    if paragraph_buffer:
        paragraph_text = "".join(paragraph_buffer)
        paragraph_text = apply_color_markup(paragraph_text)  # apply color tags
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