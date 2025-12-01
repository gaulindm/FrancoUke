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
from users.models import UserPreference
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from songbook.utils.transposer import clean_chord  # ✅ Make sure this import is at the top

import json
import os
import re


# =======================
# USER PREFERENCES
# =======================
def get_user_preferences(user):
    default_prefs = {
        "primary_instrument": "ukulele",
        "secondary_instrument": None,
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
                # attempt to map older field names if your model differs
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
            "secondary_instrument": getattr(prefs, "secondary_instrument", None),
            "is_lefty": lefty_val,
            "show_alternate_chords": getattr(prefs, "is_printing_alternate_chord", False),
            "use_known_chord_filter": getattr(prefs, "use_known_chord_filter", False),
            "known_chords": getattr(prefs, "known_chords", []),
        }
    except Exception:
        return default_prefs


# =======================
# CHORD COMPARISON (enharmonic-aware)
# =======================
def chord_equivalent(a: str, b: str) -> bool:
    """
    Compare two chord names intelligently:
    - remove trailing strum slashes and alternate bass (/F#)
    - normalize 'maj' and 'Δ' -> 'M' (major 7 shorthand),
      but preserve 'm' (minor) vs 'M' (major)
    - canonicalize enharmonic roots (Db -> C#, Eb -> D#, Bb -> A#, Gb -> F#, Ab -> G#)
    - treat dim <-> dim7 as equivalent (optional)
    """

    import re
    if not a or not b:
        return False

    # Basic cleanup: strip outer whitespace and trailing strum slashes
    a = re.sub(r'/+$', '', a.strip())
    b = re.sub(r'/+$', '', b.strip())

    # Remove alternate bass note (D/F# -> D)
    a = re.sub(r'/[A-G][#b]?$', '', a)
    b = re.sub(r'/[A-G][#b]?$', '', b)

    # Normalize common textual variants (maj -> M, Δ -> M)
    # Note: do NOT lowercase everything — keep M vs m distinction
    def normalize_maj_tokens(name: str) -> str:
        name = re.sub(r'(?i)maj', 'M', name)   # Amaj7 -> AM7
        name = re.sub(r'(?i)Δ', 'M', name)     # AΔ7 -> AM7
        # convert 'min' -> 'm' if present, keep explicit 'm'
        name = re.sub(r'(?i)min', 'm', name)
        return name

    a = normalize_maj_tokens(a)
    b = normalize_maj_tokens(b)

    # --------------------------------
    # Enharmonic mapping: flats -> sharps
    # --------------------------------
    # We canonicalize the root note only, leaving the rest (suffix/extensions) intact.
    ENHARMONIC_TO_SHARP = {
        'CB': 'B',  # Cb -> B
        'DB': 'C#',
        'EB': 'D#',
        'GB': 'F#',
        'AB': 'G#',
        'BB': 'A#',
        'FB': 'E',
        # keep sharps as-is
        'C#': 'C#', 'D#': 'D#', 'F#': 'F#', 'G#': 'G#', 'A#': 'A#'
    }

    # Accept common flat symbol 'b' and unicode '♭'
    def canonicalize_enharmonic(chord_name: str) -> str:
        """
        Split chord_name into root (A-G plus optional accidental) and suffix.
        Convert root flats (e.g. Db, Eb) to sharp equivalents (C#, D#).
        Return combined string (root + suffix) without lowercasing.
        """
        chord_name = chord_name.strip()
        # match root letter + optional accidental, then the rest
        m = re.match(r'^([A-Ga-g])([#b♭]?)(.*)$', chord_name)
        if not m:
            return chord_name  # can't parse — return as-is
        root_letter = m.group(1).upper()
        accidental = m.group(2).replace('♭', 'b')  # normalize unicode flat to 'b'
        rest = m.group(3) or ''

        root = root_letter + accidental  # e.g. 'D' + 'b' -> 'Db'
        # map flats to sharps (case-insensitive key)
        root_key = root.upper()
        if root_key in ENHARMONIC_TO_SHARP:
            root_canonical = ENHARMONIC_TO_SHARP[root_key]
        else:
            # if not in map, keep original root (covers natural notes and sharps)
            root_canonical = root_letter + accidental

        return f"{root_canonical}{rest}"

    a_can = canonicalize_enharmonic(a)
    b_can = canonicalize_enharmonic(b)

    # --------------------------------
    # Diminished alias: treat dim <-> dim7 as equal
    # --------------------------------
    # Normalize whitespace
    a_can = a_can.strip()
    b_can = b_can.strip()

    # Quick direct equality first
    if a_can == b_can:
        return True

    # treat Ddim and Ddim7 as equivalent
    if re.match(r'^[A-G][#]?[dD]im$', a_can) and re.match(r'^[A-G][#]?[dD]im7$', b_can):
        return True
    if re.match(r'^[A-G][#]?[dD]im7$', a_can) and re.match(r'^[A-G][#]?[dD]im$', b_can):
        return True

    # Finally, compare normalized names exactly (case sensitive to preserve M vs m)
    return a_can == b_can

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

        # 👇 Default alignment logic
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
        "centered": create_style("centered"),  # ✅ Has same logic — defaults to center
    }

# =======================
# LOAD RELEVANT CHORDS
# =======================
def load_relevant_chords(songs, user_prefs, transpose_value):
    """
    Instrument-aware: try matching transposed chords first against PRIMARY
    instrument chord set, then SECONDARY. Preserve requested_name and
    ensure instrument is set on each returned chord_def copy.
    """
    primary_inst = user_prefs.get("primary_instrument")
    secondary_inst = user_prefs.get("secondary_instrument")

    chords_primary = load_chords(primary_inst or "ukulele")
    chords_secondary = load_chords(secondary_inst) if secondary_inst else []

    # mark instrument on each loaded chord (safe copy)
    for c in chords_primary:
        c["instrument"] = primary_inst
    for c in chords_secondary:
        c["instrument"] = secondary_inst

    all_chords = chords_primary + chords_secondary

    # extract used chords (from first song as before)
    raw_used = extract_used_chords(songs[0].lyrics_with_chords)
    # normalize & transpose
    used_cleaned = [normalize_chord(clean_chord(ch)).strip() for ch in raw_used]
    transposed_chords = {
        transpose_chord(clean_chord(ch).strip(), transpose_value).strip()
        for ch in used_cleaned
    }

    relevant_chords = []
    added_keys = set()  # track (canonical_name, instrument) to avoid dup per instrument

    for t_chord in transposed_chords:
        if not t_chord:
            continue

        matched = False

        # 1) Try primary instrument only
        for chord_def in chords_primary:
            try:
                if chord_equivalent(chord_def.get("name", ""), t_chord):
                    key = (chord_def.get("name", "").lower(), primary_inst)
                    if key not in added_keys:
                        chord_copy = dict(chord_def)
                        chord_copy["requested_name"] = t_chord
                        chord_copy["instrument"] = primary_inst
                        relevant_chords.append(chord_copy)
                        added_keys.add(key)
                    matched = True
                    break
            except Exception:
                # don't let one bad chord definition stop the loop
                continue

        if matched:
            continue

        # 2) Try secondary instrument only
        if secondary_inst:
            for chord_def in chords_secondary:
                try:
                    if chord_equivalent(chord_def.get("name", ""), t_chord):
                        key = (chord_def.get("name", "").lower(), secondary_inst)
                        if key not in added_keys:
                            chord_copy = dict(chord_def)
                            chord_copy["requested_name"] = t_chord
                            chord_copy["instrument"] = secondary_inst
                            relevant_chords.append(chord_copy)
                            added_keys.add(key)
                        break
                except Exception:
                    continue

    return relevant_chords


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

    # --- Capo & Recording Info (improved logic) ---
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

    # --- Slash chord detection for / = one strum ---
    def contains_slash_chord(lyrics_with_chords):
        used_chords = extract_used_chords(lyrics_with_chords)
        return any('/' in chord for chord in used_chords)

    has_slash_chord = contains_slash_chord(song.lyrics_with_chords)

    # --- Normalize metadata (avoid showing 'None') ---
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
        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Bottom-align 1st and 3rd cell of top row
        ('VALIGN', (0, 0), (0, 0), 'BOTTOM'),
        ('VALIGN', (2, 0), (2, 0), 'BOTTOM'),

        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),

        # Debug grid (optional)
         #('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
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

    Features:
    - Handles all {soX}/{eoX} section directives (Intro, Verse, Chorus, Bridge, etc.)
    - New {sos}/{eos} = "Centered" section type (uses two-column table with empty label)
    - Inline {instruction: ...} directives shown under section label (compact format)
    - Consistent padding control for spacing between sections
    """

    from reportlab.platypus import Paragraph, Table, TableStyle, Spacer

    elements = []
    paragraph_buffer = []
    section_type = None
    section_instruction = None  # holds inline instruction(s) for current section

    # Map directives per site
    directive_map = {
        "FrancoUke": {
            "{soi}": "Intro",
            "{soc}": "Refrain",
            "{sov}": "Couplet",
            "{sob}": "Pont",
            "{soo}": "Outro",
            "{sod}": "Interlude",
            "{sos}": "Centered",  # ✅ new centered section
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

    # -----------------------------------
    # Helper: Flush current paragraph buffer
    # -----------------------------------
    def flush_buffer():
        nonlocal paragraph_buffer, section_type, section_instruction

        if not paragraph_buffer:
            return

        paragraph_text = "".join(paragraph_buffer)
        paragraph_text = apply_color_markup(paragraph_text)
        style = styles_dict.get(section_type.lower(), styles_dict["verse"]) if section_type else styles_dict["verse"]

        # =====================
        # Non-verse sections
        # =====================
        if section_type and section_type.lower() != "verse":
            # Label + optional instruction (in smaller gray italics)
            label_html = ""
            if section_type.lower() != "centered":
                label_html = f"<b>{section_type}:</b>"
                if section_instruction:
                    label_html += f"<br/><font size='9' color='gray'><i>{section_instruction}</i></font>"
            else:
                # For centered sections, leave label cell blank but keep two-column structure
                label_html = ""

            label_para = Paragraph(label_html, base_style)
            lyrics_para = Paragraph(paragraph_text, style)

            # Table with two columns: label (or empty), lyrics
            section_table = Table(
                [[label_para, lyrics_para]],
                colWidths=[60, 500],
                hAlign="CENTER",
            )

            # Table style — compact and optional debug grid
            section_table.setStyle(TableStyle([
                #('GRID', (0, 0), (-1, -1), 0.25, colors.grey),  # uncomment for debugging
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            elements.append(section_table)
            # Add small spacer (instead of spaceBefore/spaceAfter)
            elements.append(Spacer(1, 4))

        # =====================
        # Verse sections
        # =====================
        else:
            elements.append(Paragraph(paragraph_text, style))
            elements.append(Spacer(1, 6))

        # Reset buffers
        paragraph_buffer = []
        section_instruction = None

    # -----------------------------------
    # Main parse loop
    # -----------------------------------
    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                directive = item["directive"].lower()

                # Section boundary
                if directive in selected_map:
                    flush_buffer()
                    section_type = selected_map[directive]
                    continue

            elif "instruction" in item:
                # Capture inline instruction for this section
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

    # Flush last section
    flush_buffer()

    return elements


# =======================
# PDF GENERATION
# =======================
def draw_footer_with_doc(canvas, doc):
    draw_footer(
        canvas, doc, doc.relevant_chords, doc.chord_spacing, doc.row_spacing, doc.is_lefty,
        instrument=doc.instrument,
        secondary_instrument=doc.secondary_instrument,
        is_printing_alternate_chord=doc.is_printing_alternate_chord,
        acknowledgement=doc.acknowledgement
    )


def generate_songs_pdf(response, songs, user, transpose_value=0, formatting=None, site_name="FrancoUke"):
    def calculate_diagram_rows(chords, max_chords_per_row=8):
        return (len(chords) + max_chords_per_row - 1) // max_chords_per_row

    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=2, bottomMargin=80, leftMargin=20, rightMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    user_prefs = get_user_preferences(user)
    relevant_chords = load_relevant_chords(songs, user_prefs, transpose_value)
    print("RELEVANT CHORDS BEFORE FILTER:", relevant_chords)

    # Apply known-chord filter if enabled
    if user_prefs.get("use_known_chord_filter", False):
        known_set = set([normalize_chord(ch).lower() for ch in user_prefs.get("known_chords", [])])
        filtered_chords = []
        for chord_def in relevant_chords:
            chord_name_normalized = normalize_chord(chord_def["name"]).lower()
            if chord_name_normalized not in known_set:
                filtered_chords.append(chord_def)
        relevant_chords = filtered_chords
        print("RELEVANT CHORDS AFTER FILTER:", relevant_chords)


    # attach relevant chords and user prefs to doc for footer drawing
    doc.relevant_chords = relevant_chords
    doc.instrument = user_prefs["primary_instrument"]
    doc.secondary_instrument = user_prefs["secondary_instrument"]
    doc.row_spacing = 70
    doc.is_lefty = user_prefs.get("is_lefty", False)
    doc.acknowledgement = getattr(songs[0], "acknowledgement", "")

    # --- split relevant chords by instrument (exactly as draw_footer expects) ---
    primary_chords = [c for c in relevant_chords if c.get("instrument") == user_prefs["primary_instrument"]]
    secondary_chords = [c for c in relevant_chords if user_prefs["secondary_instrument"] and c.get("instrument") == user_prefs["secondary_instrument"]]

    # Decide how many diagrams per row: single-instrument allows more per row
    max_per_row = 14 if not user_prefs["secondary_instrument"] else 6

    def rows_needed(group):
        return 0 if not group else (len(group) + max_per_row - 1) // max_per_row

    primary_rows = rows_needed(primary_chords)
    secondary_rows = rows_needed(secondary_chords)
    rows = max(primary_rows, secondary_rows)

    # Auto-tighten chord_spacing based on how many diagrams we need per column:
    # - If many diagrams per column, tighten spacing; otherwise keep roomy spacing.
    if user_prefs["secondary_instrument"]:
        # two columns: decide based on the larger of the two columns
        largest_col_count = max(len(primary_chords), len(secondary_chords))
    else:
        largest_col_count = len(primary_chords)

    if largest_col_count <= 6:
        doc.chord_spacing = 60
    elif largest_col_count <= 10:
        doc.chord_spacing = 48
    elif largest_col_count <= 14:
        doc.chord_spacing = 42
    else:
        doc.chord_spacing = 6


    # ensure doc has minimum sensible values
    doc.chord_spacing = int(doc.chord_spacing)
    doc.row_spacing = int(doc.row_spacing or 70)

    # compute diagram area height and ensure bottom margin allows diagrams to render
    diagram_height = rows * doc.row_spacing
    # keep a minimum extra padding so footer doesn't collide with content
    doc.bottomMargin = max(80, 20 + diagram_height)



    formatting = formatting or SongFormatting.objects.filter(user=user, song=songs[0]).first()
    if not formatting:
        formatting = SongFormatting.objects.filter(user__username="Gaulind", song=songs[0]).first()

    styles_dict = get_paragraph_styles(formatting)

    for song in songs:
        elements.extend(build_song_elements(song, styles, styles_dict, site_name))
        elements.append(PageBreak())


    print("USER:", user)
    is_auth = bool(user and getattr(user, "is_authenticated", False))
    print("AUTHENTICATED:", is_auth)



    print("PDF USER PREFS:", user_prefs)


    doc.build(
    elements,
    onFirstPage=lambda c, d: draw_footer(
        c, d,
        relevant_chords,
        chord_spacing=doc.chord_spacing,
        row_spacing=doc.row_spacing,
        is_lefty=doc.is_lefty,
        instrument=doc.instrument,
        secondary_instrument=doc.secondary_instrument,
        is_printing_alternate_chord=bool(user_prefs["show_alternate_chords"]),
        acknowledgement=doc.acknowledgement
    ),

    onLaterPages=lambda c, d: draw_footer(
        c, d,
        relevant_chords,
        chord_spacing=doc.chord_spacing,
        row_spacing=doc.row_spacing,
        is_lefty=doc.is_lefty,
        instrument=doc.instrument,
        secondary_instrument=doc.secondary_instrument,
        is_printing_alternate_chord=bool(user_prefs["show_alternate_chords"]),
        acknowledgement=doc.acknowledgement
    )
)
