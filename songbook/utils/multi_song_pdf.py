# songbook/utils/multi_song_pdf.py
"""
One PDF containing many songs, each rendered correctly on its own.

Why this exists: generate_songs_pdf() builds ONE document with ONE footer, so
given several songs it draws the first song's chord diagrams (and
acknowledgement / revision date / formatting / bottom margin) on every page.

So instead, every song is rendered on its own by the existing, proven
`generate_songs_pdf` (each song gets its own footer and margin), and the
pieces are merged in order with pypdf. Nothing in here knows how to draw a
song: change how songs look in pdf_generator.py and this picks it up.

Used by:  setlist.setlist_pdf (a setlist)  and  generate_multi_song_pdf (a tag).

Requires:  pip install pypdf
"""
import logging
import math
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from songbook.models import SongFormatting
from songbook.utils.pdf_generator import generate_songs_pdf

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# 🔧 TUNE — contents page
# -----------------------------------------------------------------------
CONTENTS_TITLE_SIZE = 28
CONTENTS_SUBTITLE_SIZE = 14
CONTENTS_ENTRY_SIZE = 18          # big on purpose: easy to read on paper
CONTENTS_ENTRY_LEADING = 28
CONTENTS_FIRST_PAGE_ENTRIES = 18  # entries that fit under the title block
CONTENTS_NEXT_PAGE_ENTRIES = 24   # entries on continuation pages

# -----------------------------------------------------------------------
# 🔧 TUNE — page numbers stamped onto every page
# -----------------------------------------------------------------------
PAGE_NUMBER_SIZE = 10
PAGE_NUMBER_RIGHT_MARGIN = 24     # points from the right edge
PAGE_NUMBER_BASELINE = 10         # points up from the bottom edge

# Settings forced on for a handout, regardless of who presses the button.
# A "known chords" filter makes sense on a personal screen, but on a handout
# it would silently leave chord diagrams off the page for everybody else.
HANDOUT_PREFS = {"use_known_chord_filter": False}

# -----------------------------------------------------------------------
# 🔧 TUNE — large print
# -----------------------------------------------------------------------
# Multiplies every section's font_size (and, because leading is
# line_spacing x font_size, the line height too). 13pt default -> ~17pt.
LARGE_PRINT_SCALE = 1.3
DEFAULT_FONT_SIZE = 13            # same default as get_paragraph_styles()
FORMATTING_SECTIONS = ("intro", "verse", "chorus", "bridge",
                       "interlude", "outro", "centered")
FALLBACK_FORMATTING_USERNAME = "Gaulind"   # mirrors generate_songs_pdf()


# -----------------------------------------------------------------------
# Large print: a scaled stand-in for SongFormatting
# -----------------------------------------------------------------------
class _ScaledFormatting:
    """Looks like a SongFormatting to get_paragraph_styles(), which only does
    getattr(formatting, section) for each section name. Nothing is saved to
    the database."""

    def __init__(self, base, scale):
        for section in FORMATTING_SECTIONS:
            cfg = dict(getattr(base, section, None) or {})
            size = cfg.get("font_size", DEFAULT_FONT_SIZE)
            cfg["font_size"] = round(size * scale, 1)
            setattr(self, section, cfg)


def _large_print_formatting(song, user, scale):
    # Same lookup order as generate_songs_pdf(): the user's own formatting
    # for this song, then the fallback user's, then plain defaults.
    qs = SongFormatting.objects.filter(song=song)
    base = qs.filter(user=user).first() if user else None
    base = base or qs.filter(user__username=FALLBACK_FORMATTING_USERNAME).first()
    return _ScaledFormatting(base, scale)   # base may be None -> defaults


# -----------------------------------------------------------------------
# One song  ->  PDF bytes
# -----------------------------------------------------------------------
def _render_song_pdf(song, user, site_name, large_print=False):
    formatting = (_large_print_formatting(song, user, LARGE_PRINT_SCALE)
                  if large_print else None)
    buf = BytesIO()
    generate_songs_pdf(
        buf,
        [song],
        user=user,
        transpose_value=0,
        formatting=formatting,
        site_name=site_name,
        prefs_override=HANDOUT_PREFS,
    )
    return buf.getvalue()


def _render_error_page(title):
    """Visible placeholder, so a song that fails never disappears silently."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(w / 2, h - 120, title or "Untitled Song")
    c.setFont("Helvetica", 14)
    c.drawCentredString(w / 2, h - 160, "This song could not be printed.")
    c.drawCentredString(w / 2, h - 182, "Please tell the group leader.")
    c.save()
    return buf.getvalue()


# -----------------------------------------------------------------------
# Contents page(s)
# -----------------------------------------------------------------------
def _contents_page_count(n_entries):
    if n_entries <= CONTENTS_FIRST_PAGE_ENTRIES:
        return 1
    rest = n_entries - CONTENTS_FIRST_PAGE_ENTRIES
    return 1 + math.ceil(rest / CONTENTS_NEXT_PAGE_ENTRIES)


def _render_contents_pdf(doc_title, subtitle_lines, entries):
    """entries: list of (title, page_number). Returns PDF bytes."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    left = 60
    right = w - 60

    def draw_entries(items, start_index, y_top):
        y = y_top
        c.setFont("Helvetica", CONTENTS_ENTRY_SIZE)
        for i, (title, page) in enumerate(items, start=start_index):
            label = f"{i}.  {title}"
            # Trim a very long title rather than run into the page number.
            max_w = right - left - 50
            if c.stringWidth(label, "Helvetica", CONTENTS_ENTRY_SIZE) > max_w:
                while c.stringWidth(label + "...", "Helvetica", CONTENTS_ENTRY_SIZE) > max_w:
                    label = label[:-1]
                label = label.rstrip() + "..."
            c.drawString(left, y, label)
            c.drawRightString(right, y, str(page))
            y -= CONTENTS_ENTRY_LEADING

    # First page: title block
    y = h - 90
    c.setFont("Helvetica-Bold", CONTENTS_TITLE_SIZE)
    c.drawCentredString(w / 2, y, doc_title)
    y -= 30
    c.setFont("Helvetica", CONTENTS_SUBTITLE_SIZE)
    for line in subtitle_lines:
        c.drawCentredString(w / 2, y, line)
        y -= 20
    y -= 24

    first = entries[:CONTENTS_FIRST_PAGE_ENTRIES]
    draw_entries(first, 1, y)
    index = 1 + len(first)
    remaining = entries[CONTENTS_FIRST_PAGE_ENTRIES:]

    while remaining:
        c.showPage()
        chunk = remaining[:CONTENTS_NEXT_PAGE_ENTRIES]
        draw_entries(chunk, index, h - 90)
        index += len(chunk)
        remaining = remaining[CONTENTS_NEXT_PAGE_ENTRIES:]

    c.save()
    return buf.getvalue()


# -----------------------------------------------------------------------
# Page-number stamp
# -----------------------------------------------------------------------
def _stamp_page_numbers(writer, skip_first=0):
    """Write the page number on every page after the first `skip_first`."""
    for idx, page in enumerate(writer.pages):
        if idx < skip_first:
            continue
        pw = float(page.mediabox.width)
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=(pw, float(page.mediabox.height)))
        c.setFont("Helvetica", PAGE_NUMBER_SIZE)
        c.drawRightString(pw - PAGE_NUMBER_RIGHT_MARGIN, PAGE_NUMBER_BASELINE, str(idx + 1))
        c.save()
        buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0])


# -----------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------
def build_songs_pdf(songs, title, subtitle_lines=(), user=None, site_name=None,
                    contents_page=True, page_numbers=True, large_print=False):
    """
    Return the PDF bytes for `songs`, in the order given.

    title          shown on the contents page and used as the PDF's title
    subtitle_lines short lines under the title (a date, a place, "12 songs"...)
    user           may be None (anonymous): the generator then falls back to
                   its default preferences and default formatting, exactly as
                   preview_pdf does.
    """
    songs = list(songs)

    rendered = []   # (title, pdf_bytes, page_count)
    for song in songs:
        try:
            data = _render_song_pdf(song, user, site_name, large_print)
        except Exception:
            logger.exception("Multi-song PDF '%s': could not render song %s (%s)",
                             title, song.pk, song.songTitle)
            data = _render_error_page(song.songTitle)
        rendered.append((song.songTitle or "Untitled Song", data,
                         len(PdfReader(BytesIO(data)).pages)))

    # Work out where each song starts (needed for the contents page).
    n_contents = _contents_page_count(len(rendered)) if (contents_page and rendered) else 0
    entries = []
    next_page = n_contents + 1            # 1-based page number
    for song_title, _data, n_pages in rendered:
        entries.append((song_title, next_page))
        next_page += n_pages

    writer = PdfWriter()

    if n_contents:
        contents = _render_contents_pdf(title, list(subtitle_lines), entries)
        for page in PdfReader(BytesIO(contents)).pages:
            writer.add_page(page)

    for (song_title, data, _n), (_t, start_page) in zip(rendered, entries):
        for page in PdfReader(BytesIO(data)).pages:
            writer.add_page(page)
        # Bookmark, handy when the PDF is read on a screen.
        writer.add_outline_item(song_title, start_page - 1)

    if page_numbers:
        _stamp_page_numbers(writer, skip_first=n_contents)

    writer.add_metadata({"/Title": title})

    out = BytesIO()
    writer.write(out)
    return out.getvalue()