"""
cal_pdf_generator.py  --  "CAL" = Chords Above Lyrics.

A second PDF format for the songbook. Same page, same title block, same chord
diagrams in the footer, same sections ({soc}, {sov}, {page}, ...) as
pdf_generator.py, but the chords are printed on their own line ABOVE the
syllable they belong to, instead of inline in square brackets:

        C            F
        Don't worry about a thing

Page breaks in this format
- {calpage} starts a new page in THIS format only. The standard PDF ignores it,
  just as this format ignores {page} once a song has a {calpage}. That lets one
  song carry both: {page} where the inline layout should break, {calpage} where
  the chords-above layout should break (its lines are taller, so the breaks
  fall in different places).
- A song with no {calpage} at all falls back to its {page} tags.

Formatting (font size, line spacing, space before/after, alignment, ...)
- SongFormatting gets a JSON field named "cal" that holds the formatting for THIS
  format, in the same shape as its "verse" / "chorus" / ... fields:
      {"verse": {"font_size": 15, "line_spacing": 1.3, "alignment": "left"}, ...}
- Any section or setting missing from "cal" falls back to the standard
  formatting (CAL_FALL_BACK_TO_STANDARD below). Until the field exists, or while
  it is empty, this format simply uses the standard formatting.

Put this file in the same folder as pdf_generator.py (it imports from it).
Use it exactly like the standard generator:

    from .cal_pdf_generator import generate_songs_pdf as generate_cal_pdf
    generate_cal_pdf(response, songs, user, transpose_value=0, site_name="FrancoUke")

(The file name must not contain a hyphen, e.g. "CAL-PDF_generator.py", because
Python cannot import such a name.)

What is shared, and what is a copy
- Shared (imported from pdf_generator.py): the title block, preferences,
  section styles, tabs, page-number markers, colour markup, constants.
  Change those there and CAL follows.
- Copied: generate_songs_pdf() below (document set-up, chord loading, footer),
  and the {soc}/{sov}... directive names. If you change those in
  pdf_generator.py, make the same change here.
"""
import re
from functools import partial
from types import SimpleNamespace

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer, Table, TableStyle

from songbook.models import SongFormatting
from songbook.utils.transposer import normalize_chord
from songbook.utils.chords.loader import load_relevant_chords
from songbook.utils.chords.drawer import draw_footer, compute_footer_min_bottom_margin

from .pdf_generator import (
    get_user_preferences, get_paragraph_styles, build_song_elements,
    apply_color_markup, build_tab_flowable,
    SongStartMarker, SongPageCanvas,
    TOP_MARGIN, LEFT_MARGIN, RIGHT_MARGIN, CONTINUATION_TOP_MARGIN,
    LABEL_COL_WIDTH, LYRICS_COL_WIDTH, TAB_COLUMN_WIDTH, TAB_PADDING, TAB_BACKGROUND,
    COUNT_CUE_RE, VOCAL_GROUP_RE, VOCAL_GROUP_LABEL, VOCAL_GROUP_COLORS,
    VOCAL_GROUP_DEFAULT_COLOR, INLINE_COMMENT_RE, ECHO_RE, ECHO_INDENT_SPACES,
)


# =======================
# TUNING
# =======================
CAL_CHORD_SCALE = 1.0       # 🔧 chord size relative to the lyric size
CAL_CHORD_GAP = 5           # 🔧 minimum points between two chords on the same line
CAL_CHORD_ROW_FACTOR = 1.15 # 🔧 height of the chord row = chord size x this
CAL_LINE_GAP = 3            # 🔧 extra space under each lyric line
CAL_NOTE_GAP = 8            # gap between the lyrics and a count cue / note at the end of the line
CAL_VG_FONT_SIZE = 8        # size of the "VG 1:" label
CAL_FALL_BACK_TO_STANDARD = True   # settings missing from SongFormatting.cal come from the standard formatting
_FORMATTING_SECTIONS = ("intro", "verse", "chorus", "bridge", "interlude", "outro", "centered")


def _cal_formatting(formatting):
    """The formatting to use for this format, shaped like a SongFormatting.

    For each section: the standard settings (as a base, if allowed) with the
    settings stored in formatting.cal laid on top.
    """
    cal = getattr(formatting, "cal", None) or {}
    chosen = {}
    for section in _FORMATTING_SECTIONS:
        base = (getattr(formatting, section, None) or {}) if CAL_FALL_BACK_TO_STANDARD else {}
        chosen[section] = {**base, **(cal.get(section) or {})}
    return SimpleNamespace(**chosen)


# =======================
# SMALL HELPERS
# =======================
_FONT_VARIANTS = {
    "Helvetica":   {"bold": "Helvetica-Bold", "italic": "Helvetica-Oblique", "bolditalic": "Helvetica-BoldOblique"},
    "Times-Roman": {"bold": "Times-Bold",     "italic": "Times-Italic",      "bolditalic": "Times-BoldItalic"},
    "Courier":     {"bold": "Courier-Bold",   "italic": "Courier-Oblique",   "bolditalic": "Courier-BoldOblique"},
}


def _variant(font, kind):
    return _FONT_VARIANTS.get(font, _FONT_VARIANTS["Helvetica"])[kind]


def _to_color(value, default=colors.black):
    try:
        return colors.toColor(value) or default
    except Exception:
        return default


_TOKEN_RE = re.compile(r"(<[^>]*>|\x01\d+\x02)")
_FG_RE = re.compile(r"(?<![A-Za-z])color\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
_BG_RE = re.compile(r"backColor\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)


def _parse_markup(marked):
    """Turn text with <font ...> tags and chord markers into plain text.

    Returns (plain, chunks, positions):
      plain      the text with every tag removed
      chunks     [(start, end, text_colour, background_colour)] covering plain
      positions  {chord number: index in plain where that chord sits}
    """
    plain = ""
    chunks = []
    positions = {}
    stack = [(None, None)]
    for token in _TOKEN_RE.split(marked):
        if not token:
            continue
        if token[0] == "\x01":
            positions[int(token[1:-1])] = len(plain)
        elif token[0] == "<":
            low = token.lower()
            if low.startswith("<font"):
                fg = _FG_RE.search(token)
                bg = _BG_RE.search(token)
                top_fg, top_bg = stack[-1]
                stack.append((fg.group(1) if fg else top_fg, bg.group(1) if bg else top_bg))
            elif low.startswith("</font"):
                if len(stack) > 1:
                    stack.pop()
            # any other tag is dropped
        else:
            text = (token.replace("&nbsp;", " ").replace("&lt;", "<")
                         .replace("&gt;", ">").replace("&amp;", "&"))
            fg, bg = stack[-1]
            chunks.append((len(plain), len(plain) + len(text), fg, bg))
            plain += text
    return plain, chunks, positions


# =======================
# ONE LYRIC LINE WITH ITS CHORDS
# =======================
class ChordLyricLine(Flowable):
    """One sung line: chord names on a row above, lyrics on the row below.

    Each chord starts exactly above the first letter it belongs to. If two
    chords would touch, the second one slides right (the lyrics never move).
    A line that is too long wraps at spaces, and every chord stays above its word.
    """
    def __init__(self, plain, chunks, chords, style, chord_color="black",
                 prefix=None, notes=None):
        super().__init__()
        self.spaceBefore = 0      # ReportLab would otherwise borrow style.spaceBefore/After
        self.spaceAfter = 0       # (12pt each) and spread the lines apart
        self.plain = plain
        self.chunks = chunks
        self.chords = sorted(chords, key=lambda c: c[0])   # (index, name, optional)
        self.style = style
        self.font = style.fontName
        self.size = style.fontSize
        self.leading = style.leading
        self.align = style.alignment
        self.text_color = _to_color(style.textColor)
        self.chord_color = _to_color(chord_color)
        self.chord_size = self.size * CAL_CHORD_SCALE
        self.prefix = prefix              # (label, hex colour) for vocal groups, or None
        self.notes = list(notes or [])    # [(text, "cue" | "note")]
        self.echo = None                  # text of an {c:echo: ...} line under this one
        self._rows = []
        self._height = 0

    # ---- measuring -------------------------------------------------------
    def _w(self, text, font=None, size=None):
        return stringWidth(text, font or self.font, size or self.size)

    def _prefix_width(self):
        if not self.prefix:
            return 0
        return stringWidth(self.prefix[0], _variant(self.font, "bold"), CAL_VG_FONT_SIZE) + 4

    def _notes_width(self):
        total = 0
        for text, kind in self.notes:
            font = _variant(self.font, "bolditalic") if kind == "cue" else _variant(self.font, "italic")
            size = self.size if kind == "cue" else 9
            total += CAL_NOTE_GAP + stringWidth(text, font, size)
        return total

    def _ranges(self, avail):
        """Split the text into rows that fit; one row if everything fits."""
        plain = self.plain
        extra = self._prefix_width() + self._notes_width()
        if self._w(plain) + extra <= avail or not plain.strip() or " " not in plain.strip():
            return [(0, len(plain))]
        words = [(m.start(), m.end()) for m in re.finditer(r"\S+", plain)]
        ranges = []
        a, b = 0, words[0][1]
        for ws, we in words[1:]:
            lead = self._prefix_width() if not ranges else 0
            if self._w(plain[a:we]) + lead <= avail:
                b = we
            else:
                ranges.append((a, b))
                a, b = ws, we
        ranges.append((a, b))
        return ranges

    def wrap(self, avail_width, avail_height):
        ranges = self._ranges(avail_width)
        self._rows = []
        for i, (a, b) in enumerate(ranges):
            next_a = ranges[i + 1][0] if i + 1 < len(ranges) else len(self.plain) + 1
            last = (i == len(ranges) - 1)
            text_w = self._w(self.plain[a:b])
            placed, prev_end = [], -1e9
            for idx, name, optional in self.chords:
                if not (a <= idx < next_a or (i == 0 and idx < a)):
                    continue
                x = self._w(self.plain[a:min(max(idx, a), b)])
                font = _variant(self.font, "italic") if optional else _variant(self.font, "bold")
                cw = stringWidth(name, font, self.chord_size)
                x = max(x, prev_end + CAL_CHORD_GAP)
                placed.append((x, name, optional))
                prev_end = x + cw
            chord_extent = prev_end if placed else 0
            lead = self._prefix_width() if i == 0 else 0
            trail = self._notes_width() if last else 0
            width = max(lead + text_w + trail, lead + chord_extent)
            has_text = bool(self.plain[a:b].strip()) or (last and bool(self.notes)) or (i == 0 and bool(self.prefix))
            self._rows.append({"a": a, "b": b, "chords": placed, "width": width, "lead": lead,
                               "text_w": text_w, "last": last, "has_text": has_text})

        height = 0
        for row in self._rows:
            if row["chords"]:
                height += self.chord_size * CAL_CHORD_ROW_FACTOR
            height += self.leading if row["has_text"] else self.leading * 0.5
        if self.echo:
            height += self.leading
        height += CAL_LINE_GAP
        self._height = height
        self.width, self.height = avail_width, height
        return avail_width, height

    # ---- drawing -----------------------------------------------------------
    def _x0(self, width, avail):
        if self.align == TA_CENTER:
            return max(0, (avail - width) / 2)
        if self.align == TA_RIGHT:
            return max(0, avail - width)
        return 0

    def _baseline(self, y_top, row_h, size):
        # centre the glyph box (ascent .72 + descent .21 of the size) in the row
        return y_top - (row_h - 0.93 * size) / 2 - 0.72 * size

    def draw(self):
        c = self.canv
        avail = self.width
        y = self._height
        for row in self._rows:
            x0 = self._x0(row["width"], avail)
            x_text = x0 + row["lead"]

            if row["chords"]:
                ch_h = self.chord_size * CAL_CHORD_ROW_FACTOR
                base = self._baseline(y, ch_h, self.chord_size)
                for x, name, optional in row["chords"]:
                    if optional:
                        c.setFont(_variant(self.font, "italic"), self.chord_size)
                        c.setFillColor(colors.grey)
                    else:
                        c.setFont(_variant(self.font, "bold"), self.chord_size)
                        c.setFillColor(self.chord_color)
                    c.drawString(x_text + x, base, name)
                y -= ch_h

            if not row["has_text"]:          # chord-only line: nothing to draw below the chords
                y -= self.leading * 0.5
                continue

            base = self._baseline(y, self.leading, self.size)
            if row["lead"] and self.prefix:
                c.setFont(_variant(self.font, "bold"), CAL_VG_FONT_SIZE)
                c.setFillColor(_to_color(self.prefix[1], colors.grey))
                c.drawString(x0, base, self.prefix[0])

            a, b = row["a"], row["b"]
            for s, e, fg, bg in self.chunks:
                s2, e2 = max(s, a), min(e, b)
                if s2 >= e2:
                    continue
                px = x_text + self._w(self.plain[a:s2])
                piece = self.plain[s2:e2]
                if bg:
                    c.setFillColor(_to_color(bg, colors.yellow))
                    c.rect(px, base - 0.22 * self.size, self._w(piece), 1.05 * self.size, stroke=0, fill=1)
                c.setFont(self.font, self.size)
                c.setFillColor(_to_color(fg, self.text_color) if fg else self.text_color)
                c.drawString(px, base, piece)

            if row["last"]:
                nx = x_text + row["text_w"]
                for text, kind in self.notes:
                    nx += CAL_NOTE_GAP
                    if kind == "cue":
                        c.setFont(_variant(self.font, "bolditalic"), self.size)
                        c.setFillColor(self.text_color)
                    else:
                        c.setFont(_variant(self.font, "italic"), 9)
                        c.setFillColor(colors.grey)
                    c.drawString(nx, base, text)
                    nx += stringWidth(text, c._fontname, c._fontsize)
            y -= self.leading

        if self.echo:
            text = self.echo.strip()
            if not (text.startswith("(") and text.endswith(")")):
                text = f"({text})"
            font = _variant(self.font, "italic")
            indent = ECHO_INDENT_SPACES * self._w(" ")
            width = indent + stringWidth(text, font, self.size)
            ex = self._x0(width, avail) + indent
            c.setFont(font, self.size)
            c.setFillColor(self.text_color)
            c.drawString(ex, self._baseline(y, self.leading, self.size), text)


def _line_from_group(group, style, chord_color, pending_group):
    """Build a ChordLyricLine from one parsed line (a list of chord/lyric items)."""
    # 1. one segment per chord: [chord or None, text up to the next chord, optional?]
    segments, cur = [], None
    for item in group:
        if "chord" in item:
            cur = [item["chord"], item.get("lyric", ""), bool(item.get("optional"))]
            segments.append(cur)
        elif "lyric" in item:
            if cur is None:
                cur = [None, item["lyric"], False]
                segments.append(cur)
            else:
                cur[1] += item["lyric"]

    # 2. tidy each segment: "[C]___ " leaves just the gap; inline {c:...} become notes
    notes = []

    def grab(match):
        inner = match.group(1).strip()
        notes.append((inner, "cue" if COUNT_CUE_RE.match(inner) else "note"))
        return ""

    raw, chord_list = "", []
    for chord, text, optional in segments:
        if chord is not None:
            m = re.match(r"^_+(\s*)$", text)
            if m:
                text = m.group(1)
        text = INLINE_COMMENT_RE.sub(grab, text)
        if chord is not None:
            raw += f"\x01{len(chord_list)}\x02"
            chord_list.append((chord, optional))
        raw += text

    # 3. colour tags (<red>..</red> ...) -> plain text + coloured chunks
    plain, chunks, positions = _parse_markup(apply_color_markup(raw))
    chords = [(positions.get(k, len(plain)), name, optional)
              for k, (name, optional) in enumerate(chord_list)]
    if not plain.strip() and not chords and not notes:
        return None

    prefix = None
    if pending_group is not None:
        prefix = (VOCAL_GROUP_LABEL.format(n=pending_group),
                  VOCAL_GROUP_COLORS.get(str(pending_group), VOCAL_GROUP_DEFAULT_COLOR))
    return ChordLyricLine(plain, chunks, chords, style, chord_color=chord_color,
                          prefix=prefix, notes=notes)


# =======================
# SECTIONS (same structure as build_lyrics_elements in pdf_generator.py)
# =======================
_DIRECTIVE_MAPS = {
    "FrancoUke": {
        "{soi}": "Intro", "{soc}": "Refrain", "{sov}": "Couplet", "{sob}": "Pont",
        "{soo}": "Outro", "{sod}": "Interlude", "{sos}": "Centered", "{page}": "PAGEBREAK",
        "{eoi}": None, "{eoc}": None, "{eov}": None, "{eob}": None, "{eoo}": None,
        "{eod}": None, "{eos}": None,
    },
    "StrumSphere": {
        "{soi}": "Intro", "{soc}": "Chorus", "{sov}": "Verse", "{sob}": "Bridge",
        "{soo}": "Outro", "{sod}": "Interlude", "{sos}": "Centered", "{page}": "PAGEBREAK",
        "{eoi}": None, "{eoc}": None, "{eov}": None, "{eob}": None, "{eoo}": None,
        "{eod}": None, "{eos}": None,
    },
}


def build_cal_lyrics_elements(lyrics_with_chords, styles_dict, base_style, site_name,
                              chord_color="black"):
    """Reportlab elements for the lyrics, chords printed above the words."""
    elements = []
    lines = []                  # flowables of the section being collected
    section_type = None
    section_instruction = None
    pending_group = None        # vocal group number waiting for its lyric line
    last_line = None            # last ChordLyricLine (echo / count cue attach to it)
    section_label_shown = False
    prev_after = 0              # space-after of the previous section (gap = the larger of the two)

    selected_map = dict(_DIRECTIVE_MAPS.get(site_name, _DIRECTIVE_MAPS["StrumSphere"]))

    # Page breaks: {calpage} when the song has any (then {page} is ignored here),
    # otherwise the song's {page} tags.
    uses_calpage = any(
        isinstance(g, list) and any(str(i.get("directive", "")).strip().lower() == "{calpage}" for i in g)
        for g in lyrics_with_chords
    )
    if uses_calpage:
        selected_map.pop("{page}", None)
        selected_map["{calpage}"] = "PAGEBREAK"

    def current_style():
        key = section_type.lower() if section_type else "verse"
        return styles_dict.get(key, styles_dict["verse"])

    def comment_style():
        st = current_style()
        return ParagraphStyle("CalSongComment", parent=base_style, fontSize=st.fontSize,
                              leading=st.leading, textColor=colors.red, alignment=TA_LEFT,
                              spaceBefore=4, spaceAfter=2)

    def flush():
        nonlocal lines, section_instruction, last_line, section_label_shown, prev_after
        if not lines:
            return
        st = current_style()
        gap = max(prev_after, st.spaceBefore)       # space before this section
        if gap:
            elements.append(Spacer(1, gap))
        prev_after = st.spaceAfter                  # space after it (used by the next section)
        if section_type and section_type.lower() != "verse":
            label_html = ""
            if section_type.lower() != "centered":
                label_html = f"<b>{section_type}:</b>"
                section_label_shown = True
                if section_instruction:
                    label_html += f"<br/><font size='9' color='gray'><i>{section_instruction}</i></font>"
            table = Table([[Paragraph(label_html, base_style), lines, ""]],
                          colWidths=[LABEL_COL_WIDTH, LYRICS_COL_WIDTH, LABEL_COL_WIDTH],
                          hAlign="CENTER")
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 4))
        else:
            elements.extend(lines)
            elements.append(Spacer(1, 6))
        lines = []
        section_instruction = None
        last_line = None

    for group in lyrics_with_chords:
        # Tab block ({sot}...{eot}) arrives as a dict
        if isinstance(group, dict) and group.get("type") == "tab":
            flush()
            pending_group = None
            tab_flowable = build_tab_flowable(group.get("lines", []))
            if tab_flowable is not None:
                label_html = ""
                if (section_type and section_type.lower() not in ("verse", "centered")
                        and not section_label_shown):
                    label_html = f"<b>{section_type}:</b>"
                    if section_instruction:
                        label_html += f"<br/><font size='9' color='gray'><i>{section_instruction}</i></font>"
                        section_instruction = None
                    section_label_shown = True
                tab_table = Table([[Paragraph(label_html, base_style), tab_flowable, ""]],
                                  colWidths=[LABEL_COL_WIDTH, TAB_COLUMN_WIDTH, LABEL_COL_WIDTH],
                                  hAlign="CENTER")
                tab_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BACKGROUND', (1, 0), (1, 0), TAB_BACKGROUND),
                    ('LEFTPADDING', (0, 0), (0, 0), 2),
                    ('RIGHTPADDING', (0, 0), (0, 0), 2),
                    ('LEFTPADDING', (1, 0), (1, 0), TAB_PADDING),
                    ('RIGHTPADDING', (1, 0), (1, 0), TAB_PADDING),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(tab_table)
                elements.append(Spacer(1, 4))
            continue

        kinds = {key for item in group for key in item}

        if "directive" in kinds:
            directive = group[0]["directive"].lower()
            if directive in selected_map:
                flush()
                pending_group = None
                mapped = selected_map[directive]
                if mapped == "PAGEBREAK":
                    prev_after = 0
                    elements.append(PageBreak())
                    # same blank space at the top of the new page as the standard PDF
                    elements.append(Spacer(1, CONTINUATION_TOP_MARGIN - TOP_MARGIN))
                    section_type = None
                else:
                    section_type = mapped
                    section_label_shown = False
            continue

        if "instruction" in kinds:
            section_instruction = group[0]["instruction"]
            continue

        if "comment" in kinds:
            comment_raw = str(group[0]["comment"]).strip()

            # Vocal group tag ({c:VG1} / {c:1}): the next lyric line gets the label
            group_match = VOCAL_GROUP_RE.match(comment_raw)
            if group_match:
                pending_group = group_match.group(1)
                continue

            # Echo ({c:echo: words}): printed right under the line it belongs to
            echo_match = ECHO_RE.match(comment_raw)
            if echo_match and last_line is not None:
                last_line.echo = echo_match.group(1)
                continue

            # Count cue ({c:(234)}) on its own line: goes to the end of the line above
            if COUNT_CUE_RE.match(comment_raw) and last_line is not None:
                last_line.notes.append((comment_raw, "cue"))
                continue

            # Any other comment: a standalone red note
            flush()
            pending_group = None
            elements.append(Paragraph(f"<i>{apply_color_markup(comment_raw)}</i>", comment_style()))
            continue

        if "lyric" in kinds or "chord" in kinds:
            line = _line_from_group(group, current_style(), chord_color, pending_group)
            pending_group = None
            if line is not None:
                lines.append(line)
                last_line = line
            continue

        if "format" in kinds and group[0].get("format") == "PARAGRAPHBREAK" and lines:
            lines.append(Spacer(1, current_style().leading * 0.6))

    flush()
    return elements


def build_cal_song_elements(song, styles, styles_dict, site_name,
                            chord_color="black", show_strumming=True):
    """Title block (shared with the standard PDF) + lyrics with chords above."""
    # The standard builder returns [SongStartMarker, title block, ...lyrics].
    # Keep only the first two; the lyrics are built the CAL way below.
    top = build_song_elements(song, styles, styles_dict, site_name,
                              chord_color=chord_color, show_strumming=show_strumming)[:2]
    if len(top) != 2 or not isinstance(top[0], SongStartMarker) or not isinstance(top[1], Table):
        raise RuntimeError(
            "build_song_elements() in pdf_generator.py no longer starts with "
            "[SongStartMarker, title Table]; update build_cal_song_elements().")
    return top + build_cal_lyrics_elements(
        song.lyrics_with_chords, styles_dict, styles["BodyText"], site_name,
        chord_color=chord_color,
    )


# =======================
# PDF GENERATION (copy of generate_songs_pdf in pdf_generator.py, lyrics built the CAL way)
# =======================
def generate_songs_pdf(response, songs, user, transpose_value=0, formatting=None,
                       site_name="FrancoUke", prefs_override=None):
    """
    CAL version of generate_songs_pdf(): same arguments, same footer chord
    diagrams, but the chords are printed above the lyrics.
    """
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet

    # Build a PDF title from the song(s) being included, so that the browser's
    # built-in "Save"/"Save to Drive" buttons use a sensible filename instead
    # of falling back to a generic default.
    if songs:
        if len(songs) == 1:
            pdf_title = songs[0].songTitle or "Untitled Song"
        else:
            pdf_title = f"{songs[0].songTitle} and {len(songs) - 1} more" if songs[0].songTitle else "Songbook"
    else:
        pdf_title = "Songbook"

    styles = getSampleStyleSheet()
    elements = []

    # Load user preferences and chords. This has to happen BEFORE the
    # SimpleDocTemplate is created below, because we need to know how tall
    # the footer's chord diagrams will be (one row vs. two, one instrument
    # vs. two side-by-side columns) in order to size bottomMargin correctly.
    # bottomMargin can't be adjusted after the doc starts laying out
    # flowables, so getting this order right matters.
    user_prefs = get_user_preferences(user)
    if prefs_override:
        user_prefs = {**user_prefs, **prefs_override}
        
    # Get suggested_alternate from first song's metadata
    suggested_alternate = None
    if songs and songs[0].metadata:
        suggested_alternate = songs[0].metadata.get('suggested_alternate')

    relevant_chords = load_relevant_chords(songs, user_prefs, transpose_value, suggested_alternate)



    # Apply known-chord filter if enabled
    if user_prefs.get("use_known_chord_filter", False):
        known_set = {normalize_chord(ch).lower() for ch in user_prefs.get("known_chords", [])}
        
        # Parse which chords have explicitly requested variations
        explicitly_requested = set()
        if suggested_alternate:
            import re
            alternates = [alt.strip() for alt in suggested_alternate.split(',')]
            for alt in alternates:
                match = re.match(r"^([A-G][#b]?m?(?:add\d+)?)(?:\((\d+)\))?$", alt)
                if match:
                    explicitly_requested.add(normalize_chord(match.group(1)).lower())
        
        # Filter out known chords UNLESS they were explicitly requested
        relevant_chords = [
            chord for chord in relevant_chords
            if (normalize_chord(chord["name"]).lower() not in known_set or
                normalize_chord(chord["name"]).lower() in explicitly_requested)
        ]

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

    # Now that we know how many chord rows the footer will need (accounting
    # for one instrument or two side-by-side columns), size the page's
    # bottom margin to fit — otherwise a 2-row footer paints over lyrics
    # that were laid out assuming the old fixed 80pt margin.
    bottom_margin = compute_footer_min_bottom_margin(
        relevant_chords,
        instrument=user_prefs["primary_instrument"],
        secondary_instrument=user_prefs.get("secondary_instrument"),
        chord_spacing=chord_spacing,
        row_spacing=row_spacing,
        page_width=letter[0],
        is_printing_alternate_chord=bool(user_prefs.get("show_alternate_chords", False)),
    )

    # Prepare PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=TOP_MARGIN,
        bottomMargin=bottom_margin,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        title=pdf_title,
    )

    # Load formatting
    formatting = formatting or SongFormatting.objects.filter(user=user, song=songs[0]).first()
    if not formatting:
        formatting = SongFormatting.objects.filter(user__username="Gaulind", song=songs[0]).first()
    styles_dict = get_paragraph_styles(_cal_formatting(formatting))

    # Build elements for all songs
    for song_index, song in enumerate(songs):
        elements.extend(build_cal_song_elements(
            song, styles, styles_dict, site_name,
            chord_color=user_prefs.get("chord_color", "black"),
            show_strumming=user_prefs.get("show_strumming_pattern", True),
        ))
        if song_index < len(songs) - 1:
            elements.append(PageBreak())

    # Format the revision date once, if the song has one. Kept as a plain
    # string here (rather than passing the raw date into draw_footer) so
    # drawer.py stays free of date-formatting concerns.
    revised_on = getattr(songs[0], "revised_on", None)
    revision_date = revised_on.strftime("%b %d, %Y") if revised_on else ""

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
            secondary_instrument=user_prefs.get("secondary_instrument"),
            is_printing_alternate_chord=bool(user_prefs.get("show_alternate_chords", False)),
            acknowledgement=getattr(songs[0], "acknowledgement", ""),
            revision_date=revision_date,
        ),
        onLaterPages=lambda c, d: draw_footer(
            c, d,
            relevant_chords,
            chord_spacing=chord_spacing,
            row_spacing=row_spacing,
            is_lefty=user_prefs.get("is_lefty", False),
            instrument=user_prefs["primary_instrument"],
            secondary_instrument=user_prefs.get("secondary_instrument"),
            is_printing_alternate_chord=bool(user_prefs.get("show_alternate_chords", False)),
            acknowledgement=getattr(songs[0], "acknowledgement", ""),
            revision_date=revision_date,
        ),
        canvasmaker=partial(SongPageCanvas, site_name=site_name),
    )