from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Flowable, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
#from .chord_utils import load_chords, extract_used_chords, draw_footer, ChordDiagram
from songbook.models import SongFormatting
from songbook.utils.transposer import transpose_chord, normalize_chord
from users.models import UserPreference
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
#from songbook.utils.transposer import clean_chord
#from songbook.utils.chords.normalize import normalize_variation, detect_barre, compute_base_fret
#from songbook.utils.chords.variation_rules import parse_requested_variation, select_variations
#from songbook.utils.chords.diagrams import ChordDiagram, build_chord_drawing, render_chord_svg, draw_chord_diagram
from songbook.utils.chords.loader import extract_used_chords, load_relevant_chords
from songbook.utils.chords.drawer import draw_footer


import json
import os
import re


# =======================
# USER PREFERENCES
# =======================
def get_user_preferences(user):
    default_prefs = {
        "primary_instrument": "ukulele",
        "is_lefty": False,
        "show_alternate_chords": False,
        "use_known_chord_filter": False,
        "known_chords": [],
    }

    if not user or not user.is_authenticated:
        return default_prefs

    try:
        prefs, _ = UserPreference.objects.get_or_create(
            user=user,
            defaults={
                "primary_instrument": getattr(user, "primary_instrument", "ukulele"),
            },
        )
        print("PREF OBJECT:", prefs.__dict__)

        # Allow either attribute name on the model: is_lefty or is_left_handed
        lefty_val = None
        if hasattr(prefs, "is_lefty"):
            lefty_val = getattr(prefs, "is_lefty", False)
        elif hasattr(prefs, "is_left_handed"):
            lefty_val = getattr(prefs, "is_left_handed", False)
        else:
            lefty_val = False

        return {
            "primary_instrument": prefs.primary_instrument,
            "is_lefty": lefty_val,
            "show_alternate_chords": getattr(prefs, "is_printing_alternate_chord", False),
            "use_known_chord_filter": getattr(prefs, "use_known_chord_filter", False),
            "known_chords": getattr(prefs, "known_chords", []),
        }
    except Exception:
        return default_prefs



# =======================
# COLOR MARKUP
# =======================
def apply_color_markup(text):
    color_map = {
        'red': 'red',
        'blue': 'blue',
        'green': 'green',
        'yellow': 'gold',
        'orange': 'orange',
        'pink': 'hotpink',
        'purple': 'purple',
    }
    for tag, color in color_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<font color='{color}'>{m.group(1)}</font>", text)

    short_map = {'r': 'red', 'g': 'green', 'y': 'gold'}
    for tag, color in short_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<font color='{color}'>{m.group(1)}</font>", text)

    pattern = re.compile(r'<highlight\s+color="(.*?)">(.*?)</highlight>', re.IGNORECASE | re.DOTALL)
    text = pattern.sub(lambda m: f"<font backColor='{m.group(1)}'>{m.group(2)}</font>", text)

    text = re.sub(r'<h>(.*?)</h>', r"<font backColor='yellow'>\1</font>", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"</font>\s*</font>", "</font>", text)
    return text


# =======================
# PARAGRAPH STYLES
# =======================
def get_paragraph_styles(formatting):
    styles = getSampleStyleSheet()
    base_style = styles["BodyText"]

    def create_style(section):
        config = getattr(formatting, section, {}) or {}

        # Default alignment logic
        default_alignment = "left" if section.lower() == "verse" else "center"

        return ParagraphStyle(
            name=section,
            parent=base_style,
            fontSize=config.get("font_size", 13),
            textColor=config.get("font_color", "#000000"),
            fontName=(
                config.get("font_family", "Helvetica")
                if config.get("font_family", "Helvetica") in ["Helvetica", "Times-Roman", "Courier"]
                else "Helvetica"
            ),
            leading=config.get("line_spacing", 1.2) * config.get("font_size", 13),
            spaceBefore=config.get("spacing_before", 12),
            spaceAfter=config.get("spacing_after", 12),
            alignment={
                "left": TA_LEFT,
                "center": TA_CENTER,
                "right": TA_RIGHT,
            }.get(config.get("alignment", default_alignment), TA_CENTER),
        )

    # Return style dictionary
    return {
        "intro": create_style("intro"),
        "verse": create_style("verse"),
        "chorus": create_style("chorus"),
        "bridge": create_style("bridge"),
        "interlude": create_style("interlude"),
        "outro": create_style("outro"),
        "centered": create_style("centered"),
    }


# =======================
# SONG ELEMENTS
# =======================
def build_song_elements(song, styles, styles_dict, site_name):
    elements = []
    metadata = song.metadata or {}

    # --- Styles ---
    songwriter_style = ParagraphStyle(
        'SongwriterStyle',
        parent=styles['Normal'],
        alignment=1,
        fontSize=12,
        spaceBefore=2,
        spaceAfter=2,
    )

    recording_style = ParagraphStyle(
        'RecordingStyle',
        parent=styles['Normal'],
        alignment=1,
        fontSize=11,
        spaceBefore=2,
        spaceAfter=2,
    )

    first_vocal_note_style = ParagraphStyle(
        'FirstVocalNoteStyle',
        parent=styles['Normal'],
        fontSize=9,
        spaceBefore=2,
        spaceAfter=2,
    )

    header_instruction_style = ParagraphStyle(
        'HeaderInstructionStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=2,  # right aligned
        spaceBefore=0,
        spaceAfter=0,
    )

    count_in_style = ParagraphStyle(
        'CountInStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceBefore=2,
        spaceAfter=2,
    )

    # --- Capo & Recording Info ---
    capo_value = metadata.get('capo')
    artist = metadata.get('artist', 'Unknown Artist')
    year = metadata.get('year')

    if isinstance(capo_value, str) and capo_value.lower() == "based":
        recorded_by_text = f"Based on clip by {artist}"
        if year:
            recorded_by_text += f" ({year})"
    else:
        try:
            capo_value = int(capo_value)
        except (TypeError, ValueError):
            capo_value = 0

        if capo_value > 0:
            recorded_by_text = f"Capo ({capo_value}) to match the recording by {artist}"
        else:
            recorded_by_text = f"Matches the recording by {artist}"

        if year:
            recorded_by_text += f" ({year})"

    # --- Slash chord detection ---
    def contains_slash_chord(lyrics_with_chords):
        used_chords = extract_used_chords(lyrics_with_chords)
        return any('/' in chord for chord in used_chords)

    has_slash_chord = contains_slash_chord(song.lyrics_with_chords)

    # --- Normalize metadata ---
    for key, value in metadata.items():
        if value is None:
            metadata[key] = ""

    # --- Header table content ---
    header_data = [
        [
            Paragraph(f"{metadata.get('timeSignature', '')}", first_vocal_note_style),
            Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", styles['Title']),
            Paragraph("(/ = one strum)", header_instruction_style)
            if has_slash_chord else Paragraph("", styles['Normal']),
        ],
        [
            Paragraph(
                f"1st vocal note: {metadata.get('1stnote', '')}",
                first_vocal_note_style
            ) if metadata.get('1stnote') else Paragraph("", first_vocal_note_style),
            Paragraph(f"{metadata.get('songwriter', '')}", songwriter_style),
            Paragraph(f"{metadata.get('short_instruction_1', '')}", header_instruction_style),
        ],
        [
            Paragraph(
                f"Count in: {metadata.get('count_in', '')}",
                count_in_style
            ) if metadata.get('count_in') else Paragraph("", count_in_style),
            Paragraph(recorded_by_text, recording_style),
            Paragraph(f"{metadata.get('short_instruction_2', '')}", header_instruction_style),
        ],
    ]

    # --- Header table layout ---
    header_table = Table(header_data, colWidths=[100, 400, 100])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('VALIGN', (0, 0), (0, 0), 'BOTTOM'),
        ('VALIGN', (2, 0), (2, 0), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))

    elements.append(header_table)

    # --- Lyrics ---
    lyrics_elements = build_lyrics_elements(
        song.lyrics_with_chords, styles_dict, styles['BodyText'], site_name
    )
    elements.extend(lyrics_elements)

    return elements

# =======================
# LYRICS ELEMENTS
# =======================
def build_lyrics_elements(lyrics_with_chords, styles_dict, base_style, site_name):
    """
    Build a list of reportlab elements (Paragraphs, Tables) from parsed lyrics/chords.
    """
    from reportlab.platypus import Paragraph, Table, TableStyle, Spacer

    elements = []
    paragraph_buffer = []
    section_type = None
    section_instruction = None

    # Map directives per site
    directive_map = {
        "FrancoUke": {
            "{soi}": "Intro",
            "{soc}": "Refrain",
            "{sov}": "Couplet",
            "{sob}": "Pont",
            "{soo}": "Outro",
            "{sod}": "Interlude",
            "{sos}": "Centered",
            "{eoi}": None,
            "{eoc}": None,
            "{eov}": None,
            "{eob}": None,
            "{eoo}": None,
            "{eod}": None,
            "{eos}": None,
        },
        "StrumSphere": {
            "{soi}": "Intro",
            "{soc}": "Chorus",
            "{sov}": "Verse",
            "{sob}": "Bridge",
            "{soo}": "Outro",
            "{sod}": "Interlude",
            "{sos}": "Centered",
            "{eoi}": None,
            "{eoc}": None,
            "{eov}": None,
            "{eob}": None,
            "{eoo}": None,
            "{eod}": None,
            "{eos}": None,
        },
    }

    selected_map = directive_map.get(site_name, directive_map["StrumSphere"])

    def flush_buffer():
        nonlocal paragraph_buffer, section_type, section_instruction

        if not paragraph_buffer:
            return

        paragraph_text = "".join(paragraph_buffer)
        paragraph_text = apply_color_markup(paragraph_text)
        style = styles_dict.get(section_type.lower(), styles_dict["verse"]) if section_type else styles_dict["verse"]

        # Non-verse sections
        if section_type and section_type.lower() != "verse":
            label_html = ""
            if section_type.lower() != "centered":
                label_html = f"<b>{section_type}:</b>"
                if section_instruction:
                    label_html += f"<br/><font size='9' color='gray'><i>{section_instruction}</i></font>"
            else:
                label_html = ""

            label_para = Paragraph(label_html, base_style)
            lyrics_para = Paragraph(paragraph_text, style)

            section_table = Table(
                [[label_para, lyrics_para]],
                colWidths=[60, 500],
                hAlign="CENTER",
            )

            section_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            elements.append(section_table)
            elements.append(Spacer(1, 4))

        # Verse sections
        else:
            elements.append(Paragraph(paragraph_text, style))
            elements.append(Spacer(1, 6))

        paragraph_buffer = []
        section_instruction = None

    # Main parse loop
    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                directive = item["directive"].lower()

                if directive in selected_map:
                    flush_buffer()
                    section_type = selected_map[directive]
                    continue

            elif "instruction" in item:
                section_instruction = item["instruction"]
                continue

            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]
                if chord:
                    line = f" <b>[{chord}]</b>{lyric}" if not lyric.startswith("-") else f"<b>[{chord}]</b>{lyric}"
                else:
                    line = lyric
                paragraph_buffer.append(line)

            elif "format" in item and item["format"] == "LINEBREAK":
                paragraph_buffer.append("<br/>")

    flush_buffer()

    return elements


# =======================
# PDF GENERATION
# =======================
def generate_songs_pdf(response, songs, user, transpose_value=0, formatting=None, site_name="FrancoUke"):
    """
    Generate PDF for a list of songs for the given user.
    Draws chords in the footer for the primary instrument.
    """
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet

    # Prepare PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=2,
        bottomMargin=80,
        leftMargin=20,
        rightMargin=20
    )
    styles = getSampleStyleSheet()
    elements = []

    # Load user preferences and chords
    # Load user preferences and chords
    user_prefs = get_user_preferences(user)

    # Get suggested_alternate from first song's metadata
    suggested_alternate = None
    if songs and songs[0].metadata:
        suggested_alternate = songs[0].metadata.get('suggested_alternate')
        print(f"[PDF_GENERATOR] suggested_alternate from metadata: {suggested_alternate}")

    relevant_chords = load_relevant_chords(songs, user_prefs, transpose_value, suggested_alternate)



    print("RELEVANT CHORDS BEFORE FILTER:", relevant_chords)

    # Apply known-chord filter if enabled
    if user_prefs.get("use_known_chord_filter", False):
        known_set = {normalize_chord(ch).lower() for ch in user_prefs.get("known_chords", [])}
        relevant_chords = [
            chord for chord in relevant_chords
            if normalize_chord(chord["name"]).lower() not in known_set
        ]
        print("RELEVANT CHORDS AFTER FILTER:", relevant_chords)

    # Determine spacing based on chord count
    num_chords = len(relevant_chords)
    max_per_row = 12  # Safe to avoid cutting off chords
    if num_chords <= 6:
        chord_spacing = 60
    elif num_chords <= 10:
        chord_spacing = 48
    elif num_chords <= max_per_row:
        chord_spacing = 42
    else:
        chord_spacing = 36
    row_spacing = 70

    # Load formatting
    formatting = formatting or SongFormatting.objects.filter(user=user, song=songs[0]).first()
    if not formatting:
        formatting = SongFormatting.objects.filter(user__username="Gaulind", song=songs[0]).first()
    styles_dict = get_paragraph_styles(formatting)

    # Build elements for all songs
    for song in songs:
        elements.extend(build_song_elements(song, styles, styles_dict, site_name))
        elements.append(PageBreak())

    print("USER:", user)
    print("AUTHENTICATED:", bool(user and getattr(user, "is_authenticated", False)))
    print("PDF USER PREFS:", user_prefs)

    # Build PDF with footer
    doc.build(
        elements,
        onFirstPage=lambda c, d: draw_footer(
            c, d,
            relevant_chords,
            chord_spacing=chord_spacing,
            row_spacing=row_spacing,
            is_lefty=user_prefs.get("is_lefty", False),
            instrument=user_prefs["primary_instrument"],
            secondary_instrument=None,
            is_printing_alternate_chord=bool(user_prefs.get("show_alternate_chords", False)),
            acknowledgement=getattr(songs[0], "acknowledgement", "")
        ),
        onLaterPages=lambda c, d: draw_footer(
            c, d,
            relevant_chords,
            chord_spacing=chord_spacing,
            row_spacing=row_spacing,
            is_lefty=user_prefs.get("is_lefty", False),
            instrument=user_prefs["primary_instrument"],
            secondary_instrument=None,
            is_printing_alternate_chord=bool(user_prefs.get("show_alternate_chords", False)),
            acknowledgement=getattr(songs[0], "acknowledgement", "")
        )
    )
