"""
Import songbook PDFs -> ChordPro text (optionally saved to the database).

WHAT IS NEW (lessons from cleaning the first 538 songs)
  * Section words (Verse, Chorus, Bridge...) are only turned into tags when
    they START a line ("Chorus 1:"). Lyric words like "uni-verse" are left alone.
  * Only real chords in (round brackets) become [chords]. Words in round
    brackets, e.g. (together in harmony), stay as words. That removes the
    "damaged bracket" problem.
  * Square-bracket notes from the PDF become comments or (echoes):
      [/ = one strum] -> {c:/ = one strum}      [Ooh.] -> (Ooh.)
      [repeat & fade] -> {c:Repeat and fade}    [fade] -> {c:Fade}
  * The header lines are read and moved into the directives (timeSignature,
    1stnote, capo, year, songwriter, artist) and removed from the body.
  * Page-break junk is removed: repeated title, [page 2], ****, lone chord reminders.
  * The date line [March 25, 2019] sets revised_on and is removed.
  * songTitle no longer contains the date from the file name.
  * Every section gets its closing tag ({eov}, {eoc}...). An empty "Chorus 1:"
    becomes {c:Repeat Chorus 1}.
  * Songs already in the database (same title + site) are skipped, so a re-run
    does not make duplicates.
  * In songs with no section tags, every blank line becomes a line holding one
    space, so the parser shows a gap between groups of lines. Gaps are found from
    the vertical spacing in the PDF (GAP_FACTOR below).
  * --tag adds django-taggit tags.
  * Each song prints "CHECK:" lines for anything it was unsure about.

USAGE
  Preview only (writes .cho files next to the PDFs, database untouched):
    python manage.py import_songbook_pdf path/to/folder/

  Preview on screen only (writes nothing at all):
    python manage.py import_songbook_pdf path/to/folder/ --dry-run

  Save to the database and tag:
    python manage.py import_songbook_pdf path/to/folder/ --to-db --contributor-id=1 \
        --site-name=StrumSphere --tag=GospelAndSpirituals --origin=NBU

  File names like "Song Title (Month Day, Year).pdf" give the revised_on date.
  Remove junk first: rm -rf __MACOSX ; find . -name "._*" -delete ; find . -name ".DS_Store" -delete
"""
import difflib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pdfplumber
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from songbook.models import Song  # adjust app name

ACKNOWLEDGEMENT_TEXT = "Contribution of Heather J. Topps of the North Bay Ukulele Club"

# Name of the django-taggit field on the Song model (tags = TaggableManager()).
TAGS_FIELD = "tags"

# Name of the field on the Song model that holds where a song came from (NBU...).
ORIGIN_FIELD = "origin"

# A gap between two PDF lines bigger than GAP_FACTOR x the normal line height is
# treated as a blank line. Raise it if too many gaps appear, lower it if too few.
GAP_FACTOR = 0.5

# True: blank lines become " " in every song. False: only in songs with no
# {sov}/{soc}... tags (songs with tags keep normal blank lines between sections).
SPACE_BLANKS_IN_ALL_SONGS = False

# ---------------------------------------------------------------------------
# Chord recognition
# ---------------------------------------------------------------------------
_NOTE = r"[A-G][#b]?"
_CHORD = (
    _NOTE
    + r"(?:maj|min|dim|aug|sus|add|m|M|o|\+)?"
    + r"[0-9]*(?:sus[0-9]|add[0-9])?(?:[-#b][0-9])?"
    + r"(?:/[A-G][#b]?)?"
)
# One chord plus optional strum marks (G///), or N.C., with an optional * (optional chord)
_TOKEN = r"\*?(?:" + _CHORD + r"/*|N\.?C\.?)"
# One or more tokens joined by " - ", e.g. "G/ - D/ - F/"
_SEQ = _TOKEN + r"(?:\s*-\s*" + _TOKEN + r")*"

PAREN_CHORD_RE = re.compile(r"\(\s*(" + _SEQ + r")\s*\)")
CHORD_ONLY_RE = re.compile(r"^" + _CHORD + r"$")

# ---------------------------------------------------------------------------
# Other patterns
# ---------------------------------------------------------------------------
BRACKET_RE = re.compile(r"\[([^\[\]]*)\]")
WHOLE_BRACKET_RE = re.compile(r"^\s*\[([^\[\]]*)\]\s*$")
COUNT_CUE_RE = re.compile(r"^\d(?:[\s,]*\d)*$")
STRAY_RE = re.compile(r"^[*\s]+$")  # ****  and  * *

# Notes in these PDFs are in [square] or (round) brackets, depending on the PDF.
PAGE_RE = re.compile(
    r"^\s*(?P<pre>.*?)\s*[\[(]\s*page\s*\d+\s*[\])]\s*(?:[\[(]\s*/\s*=\s*one strum\s*[\])])?\s*$",
    re.I,
)
STRUM_ONLY_RE = re.compile(r"^\s*[\[(]\s*/\s*=\s*one strum\s*[\])]\s*$", re.I)
WHOLE_NOTE_RE = re.compile(r"^\s*[\[(]\s*([^\[\]()]+?)\s*[\])]\s*$")  # a date line
HEADER_NOTE_RE = re.compile(r"[\[(]([^\[\]()]*)[\])]")
ROUND_COUNT_RE = re.compile(r"^\s*\(\s*(\d(?:[\s,]*\d)*)\s*\)\s*$")

FADE_PATTERNS = [
    (re.compile(r"[\[(]\s*repeat\s*(?:&|and)\s*fade\s*[\])]", re.I), "Repeat and fade"),
    (re.compile(r"[\[(]\s*fade\s*[\])]", re.I), "Fade"),
]

HEADER_RE = re.compile(
    r"^\s*(?P<word>pre[\s-]?chorus|chorus|verse|bridge|intro|outro|interlude|instrumental)"
    r"(?:\s+(?P<num>\d+))?\s*(?::\s*|$)(?P<rest>.*)$",
    re.I,
)
SECTION_TAGS = {
    "intro": ("soi", "eoi"),
    "verse": ("sov", "eov"),
    "chorus": ("soc", "eoc"),
    "bridge": ("sob", "eob"),
    "outro": ("soo", "eoo"),
}
COMMENT_SECTIONS = {
    "interlude": "Interlude",
    "instrumental": "Instrumental",
    "prechorus": "Pre-chorus",
}
REPEATABLE = {"verse": "Verse", "chorus": "Chorus", "bridge": "Bridge"}

_SIGS = r"(?:4/4|3/4|2/4|6/8|12/8|2/2|cut time)"
TIME_SIG_RE = re.compile(
    r"^(" + _SIGS + r")(?:\s*(?:&|and|,)\s*(" + _SIGS + r"))?\b", re.I
)
FIRST_NOTE_RE = re.compile(r"first vocal note\s*=\s*([A-G][#b]?)", re.I)
LONE_NOTE_RE = re.compile(r"^=\s*([A-G][#b]?)$")
STRUM_RE = re.compile(r"^/\s*=\s*one strum$", re.I)
CAPO_RE = re.compile(
    r"^capo on fret (\d+)(?: to match (.+?) recording(?: in (\S+))?)?$", re.I
)
KEY_RE = re.compile(r"^key matches (.+?) recording(?: in (\S+))?$", re.I)
BASED_RE = re.compile(r"^based on (.+?) recording(?: in (\S+))?$", re.I)
REC_RE = re.compile(r"^(.+?) recording(?: in (\S+))?$", re.I)
COUNT_IN_RE = re.compile(r"^count in\s*=.*$", re.I)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def parse_date(text):
    """'March 25, 2019', 'Nov. 1, 2018', 'Sept. 5, 2019' -> date, or None."""
    t = text.strip().replace(".", "")
    t = re.sub(r"\bSept\b", "Sep", t, flags=re.I)
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"):
        try:
            return datetime.strptime(t, fmt).date()
        except ValueError:
            pass
    return None


def split_title_and_date(stem):
    """'White Christmas (September 25, 2024)' -> ('White Christmas', date)."""
    m = re.search(r"\s*\(([^()]+)\)\s*$", stem)
    if m:
        d = parse_date(m.group(1))
        if d:
            return stem[: m.start()].strip(), d
    return stem.strip(), None


def _norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def title_like(text, title, threshold=0.6):
    """True if a line of text looks like the song title (case/punctuation ignored)."""
    a, b = _norm(text), _norm(title)
    if len(a) < 4 or not b:
        return False
    if a in b or b in a:
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= threshold


def count_cue(text):
    """'2,3,4' -> '(234)'   '2,3,4, 1,2,3' -> '(234,123)'"""
    groups = [re.sub(r"[\s,]", "", g) for g in re.split(r",\s+", text.strip())]
    return "(" + ",".join(groups) + ")"


def is_blank_looking(line):
    """True for empty lines and lines holding only spaces / invisible characters."""
    return re.fullmatch(r"[\s\u200b\u200c\u200d\ufeff]*", line) is not None


def space_out_blank_lines(lines):
    """Every blank-looking line becomes a single space; repeats collapse to one."""
    out = []
    for line in lines:
        if is_blank_looking(line):
            if out and out[-1] != " ":
                out.append(" ")
        else:
            out.append(line)
    while out and out[-1] == " ":
        out.pop()
    return out


def is_chord_only(line):
    """True for lines such as '[C] [F - Dm7] [G///]' with no words."""
    rest = BRACKET_RE.sub("", line)
    return not rest.replace("-", "").strip()


# ---------------------------------------------------------------------------
# Header block (the lines before the first chord line)
# ---------------------------------------------------------------------------
@dataclass
class HeaderInfo:
    time_signature: str = ""
    first_note: str = ""
    capo: str = ""
    year: str = ""
    songwriter: str = ""
    recordings: list = field(default_factory=list)  # artists named in recording lines
    capo_artist: str = ""
    comments: list = field(default_factory=list)


def add_comment(info, text):
    if text and text not in info.comments:
        info.comments.append(text)


def classify_bracket(text, info, warnings):
    """Work out what one [bracketed note] from the header means."""
    if not text:
        return
    if STRUM_RE.match(text):
        add_comment(info, "/ = one strum")
        return
    if re.fullmatch(r"\d{4}", text):
        if not info.year:  # keep the first year (the main recording)
            info.year = text
        return
    m = CAPO_RE.match(text)
    if m:
        info.capo = m.group(1)
        if m.group(2):
            comment = f"Capo on fret {m.group(1)} to match {m.group(2)} recording"
            if m.group(3):
                comment += f" in {m.group(3)}"
            add_comment(info, comment)
            if not info.capo_artist:
                info.capo_artist = m.group(2)
        return
    m = KEY_RE.match(text)
    if m:
        comment = f"Key matches {m.group(1)} recording"
        if m.group(2):
            comment += f" in {m.group(2)}"
        add_comment(info, comment)
        info.recordings.append(m.group(1))
        return
    m = BASED_RE.match(text)
    if m:
        comment = f"Based on {m.group(1)} recording"
        if m.group(2):
            comment += f" in {m.group(2)}"
        add_comment(info, comment)
        info.recordings.append(m.group(1))
        return
    m = REC_RE.match(text)
    if m:
        comment = f"{m.group(1)} recording"
        if m.group(2):
            comment += f" in {m.group(2)}"
        add_comment(info, comment)
        info.recordings.append(m.group(1))
        return
    if COUNT_IN_RE.match(text):
        add_comment(info, text[0].upper() + text[1:])
        return
    # Unknown note: the first one is usually the songwriter.
    if not info.songwriter:
        info.songwriter = text
        warnings.append(f"songwriter taken from the header line: {text!r}")
    else:
        add_comment(info, text[0].upper() + text[1:])
        warnings.append(f"unrecognised header note kept as a comment: {text!r}")


def consume_header_line(line, info, title, warnings):
    """Read one header line. Returns False if it is really a lyric line."""
    s = line.strip()
    recognised = False

    m = TIME_SIG_RE.match(s)
    if m:
        sig = m.group(1)
        info.time_signature = "Cut time" if sig.lower() == "cut time" else sig
        if m.group(2):
            add_comment(info, f"Time signatures: {sig} & {m.group(2)}")
            warnings.append(f"two time signatures ({sig} & {m.group(2)}) - the directive holds only the first")
        s = s[m.end():].strip()
        recognised = True

    m = FIRST_NOTE_RE.search(s)
    if m:
        info.first_note = m.group(1)
        s = (s[: m.start()] + " " + s[m.end():]).strip()
        recognised = True
    else:
        m = LONE_NOTE_RE.match(s)
        if m:
            info.first_note = m.group(1)
            warnings.append(
                f"1stnote {m.group(1)} was read from a garbled header line - please confirm it"
            )
            s = ""
            recognised = True

    notes = []

    def take(mm):
        text = mm.group(1).strip()
        n = _norm(text)
        if len(n) >= 2 and n in _norm(title):
            return mm.group(0)  # part of the title, e.g. "(For Me)"
        notes.append(text)
        return " "

    s = HEADER_NOTE_RE.sub(take, s)
    for text in notes:
        recognised = True
        classify_bracket(text, info, warnings)
    rest = s.strip(" .;,")

    if rest:
        if title_like(rest, title):
            return True  # the repeated title line
        if not recognised:
            return False  # a lyric line without chords: header is over
        warnings.append(f"text in a header line was left out: {rest!r}")
    return True


# ---------------------------------------------------------------------------
# Line conversions
# ---------------------------------------------------------------------------
def convert_brackets(line):
    """
    Square brackets in the PDF text are notes or echoes, never chords.
    Returns (line, comments_to_add_after_it).
    """
    after = []
    for pattern, comment in FADE_PATTERNS:
        if pattern.search(line):
            line = pattern.sub("", line).rstrip()
            after.append(comment)
    if not line.strip():
        return "", after

    m = ROUND_COUNT_RE.match(line)
    if m:
        return "{c:" + count_cue(m.group(1)) + "}", after

    m = WHOLE_BRACKET_RE.match(line)
    if m:
        text = m.group(1).strip()
        if not text:
            return "", after
        if text.upper().replace(".", "") == "NC":
            return "[N.C.]", after
        if COUNT_CUE_RE.match(text):
            return "{c:" + count_cue(text) + "}", after
        return "{c:" + text[0].upper() + text[1:] + "}", after

    def repl(mm):
        text = mm.group(1)
        if text.strip().upper().replace(".", "") == "NC":
            return "[N.C.]"
        return "(" + text + ")"

    return BRACKET_RE.sub(repl, line), after


def convert_chords(line):
    """(C) -> [C]   (G///) -> [G///]   but (words in brackets) stay as they are."""
    line = PAREN_CHORD_RE.sub(lambda m: "[" + m.group(1) + "]", line)
    line = re.sub(r"\(\s+\)", "[ ]", line)  # "( )" is the rest marker used in some songs
    return line


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def assemble_sections(lines, warnings):
    """Put {sov}/{eov} style tags around the lines, closing each one properly."""
    out = []
    state = {"kind": None, "num": None, "open_idx": None, "has_content": False}
    seen_marker = False
    warned_intro = False

    def blank_before():
        if out and out[-1].strip() != "":
            out.append("")

    def close():
        kind = state["kind"]
        if kind is None:
            return
        while out and out[-1].strip() == "":
            out.pop()
        if state["has_content"]:
            out.append("{" + SECTION_TAGS[kind][1] + "}")
        elif kind in REPEATABLE:
            label = REPEATABLE[kind] + (f" {state['num']}" if state["num"] else "")
            out[state["open_idx"]] = "{c:Repeat " + label + "}"
        else:
            del out[state["open_idx"]]
        state.update(kind=None, num=None, open_idx=None, has_content=False)

    for line in lines:
        m = HEADER_RE.match(line)
        if m:
            seen_marker = True
            word = re.sub(r"[\s-]", "", m.group("word").lower())
            num = m.group("num")
            rest = m.group("rest").strip()
            repeat_note = rest.lower() in ("(repeat)", "repeat")
            if repeat_note:
                rest = ""
            close()
            blank_before()
            if word in SECTION_TAGS:
                out.append("{" + SECTION_TAGS[word][0] + "}")
                state.update(kind=word, num=num, open_idx=len(out) - 1, has_content=False)
                if rest:
                    out.append(rest)
                    state["has_content"] = True
                elif repeat_note and word in REPEATABLE:
                    pass  # stays empty -> becomes {c:Repeat ...}
            else:
                out.append("{c:" + COMMENT_SECTIONS[word] + "}")
                if rest:
                    out.append(rest)
            continue

        if not line.strip():
            if out and out[-1].strip() != "":
                out.append("")
            continue

        # An intro should only hold chord lines; lyrics end it.
        if (
            state["kind"] == "intro"
            and not line.startswith("{c:")
            and not is_chord_only(line)
        ):
            close()
            out.append("")
            if not warned_intro:
                warnings.append(
                    "lyrics follow the intro with no section marker - add {sov} by hand if it is a verse"
                )
                warned_intro = True

        out.append(line)
        if state["kind"] and not line.startswith("{c:"):
            state["has_content"] = True

    close()
    while out and out[-1].strip() == "":
        out.pop()

    if not seen_marker:
        warnings.append("no section markers found in the PDF - sections need adding by hand")
    else:
        warnings.append("sections run until the next marker - check where each one really ends")
    return out


# ---------------------------------------------------------------------------
# The main conversion (pure text in, ChordPro text out)
# ---------------------------------------------------------------------------
def convert_text(raw_text, title, filename_date=None):
    """Returns (chordpro_text, revised_on, warnings)."""
    warnings = []
    lines = [
        re.sub(r"[\u200b\u200c\u200d\ufeff]", "", ln.replace("\u00a0", " ")).rstrip()
        for ln in raw_text.splitlines()
    ]

    # 1. trailing date line  [March 25, 2019]
    revised_on = None
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        m = WHOLE_NOTE_RE.match(lines[-1])
        if m:
            d = parse_date(m.group(1))
            if d:
                revised_on = d
                lines.pop()
    if revised_on is None:
        revised_on = filename_date
    if revised_on is None:
        warnings.append("no revised_on date found (no date line in the PDF or in the file name)")

    # 2. header block: everything before the first chord line or section marker
    info = HeaderInfo()
    idx = 0
    while idx < len(lines) and idx < 25:
        line = lines[idx]
        if not line.strip():
            idx += 1
            continue
        if PAREN_CHORD_RE.search(line) or HEADER_RE.match(line):
            break
        if not consume_header_line(line, info, title, warnings):
            break
        idx += 1
    body = lines[idx:]

    # 3. clean the body line by line
    cleaned = []
    for raw in body:
        s = raw.strip()
        if not s:
            cleaned.append("")
            continue
        if STRAY_RE.match(s):
            continue

        pm = PAGE_RE.match(raw)
        if pm or STRUM_ONLY_RE.match(raw):
            pre = pm.group("pre") if pm else ""
            if pre and not title_like(pre, title, 0.8):
                cleaned.append(pre)  # real words before a page marker: keep them
            elif not pre and cleaned:
                prev = cleaned[-1]
                if prev.strip() and not PAREN_CHORD_RE.search(prev) and "[" not in prev and title_like(prev, title, 0.8):
                    cleaned.pop()  # the repeated title above the [page 2] marker
            continue

        if CHORD_ONLY_RE.match(s) and re.search(r"[#b0-9+]", s):
            warnings.append(f"removed a lone chord reminder line: {s!r}")
            continue

        line, after = convert_brackets(raw)
        if line:
            line = convert_chords(line)
            cleaned.append(line)
        for comment in after:
            cleaned.append("{c:" + comment + "}")

    # (Go) and (Do) look like chords but may be sung words
    for line in cleaned:
        if re.search(r"\[(?:Go|Do)\]", line):
            warnings.append(f"[Go] or [Do] may be a sung word, not a chord - please check: {line.strip()[:70]!r}")

    # unbalanced round brackets usually mean a note that was split over two lines
    for line in cleaned:
        if not line.startswith("{c:") and line.count("(") != line.count(")"):
            warnings.append(f"unbalanced ( ) on this line - please check: {line.strip()[:70]!r}")

    body_lines = assemble_sections(cleaned, warnings)
    has_tags = any(re.fullmatch(r"\{so[vcbio]\}", ln) for ln in body_lines)
    if SPACE_BLANKS_IN_ALL_SONGS or not has_tags:
        body_lines = space_out_blank_lines(body_lines)

    # 4. directives, comments, body
    artist = info.recordings[0] if info.recordings else info.capo_artist
    if artist:
        warnings.append(f"artist {artist!r} was inferred from a recording line - please confirm")

    out = [
        "{title:" + title + "}",
        "{artist:" + artist + "}",
        "{youtube:}",
        "{songwriter:" + info.songwriter + "}",
        "{capo:" + info.capo + "}",
        "{year:" + info.year + "}",
        "{1stnote:" + info.first_note + "}",
        "{timeSignature:" + info.time_signature + "}",
        "",
    ]
    if info.comments:
        out.extend("{c:" + c + "}" for c in info.comments)
        out.append("")
    out.extend(body_lines)
    return "\n".join(out), revised_on, warnings


def page_text_with_gaps(page):
    """Page text with an empty line wherever the PDF shows a visible gap between lines."""
    try:
        lines = page.extract_text_lines(return_chars=False)
    except (AttributeError, TypeError):
        return page.extract_text() or ""
    if not lines:
        return ""
    heights = sorted(ln["bottom"] - ln["top"] for ln in lines)
    typical = heights[len(heights) // 2]
    out, prev = [], None
    for ln in lines:
        if prev is not None and (ln["top"] - prev["bottom"]) > GAP_FACTOR * typical:
            out.append("")
        out.append(ln["text"])
        prev = ln
    return "\n".join(out)


def pdf_to_chordpro_text(pdf_path, title, filename_date=None):
    """Extract the text from a PDF and convert it. Returns (text, revised_on, warnings)."""
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            content = page_text_with_gaps(page)
            if content.strip():
                texts.append(content)
    if not texts:
        raise ValueError("No extractable text found in PDF.")
    return convert_text("\n".join(texts), title, filename_date)


def resolve_origin(value):
    """Check --origin against the Song model and return the value to store."""
    from django.core.exceptions import FieldDoesNotExist

    try:
        f = Song._meta.get_field(ORIGIN_FIELD)
    except FieldDoesNotExist:
        raise CommandError(
            f"The Song model has no '{ORIGIN_FIELD}' field. Change ORIGIN_FIELD at the top of this file."
        )
    if f.is_relation:
        raise CommandError(f"'{ORIGIN_FIELD}' is a link to another table, not text - this script needs adjusting.")
    if f.choices:
        for stored, label in f.flatchoices:
            if str(value).lower() in (str(stored).lower(), str(label).lower()):
                return stored
        valid = ", ".join(str(c[0]) for c in f.flatchoices)
        raise CommandError(f"--origin must be one of: {valid}")
    return value


# ---------------------------------------------------------------------------
# The management command
# ---------------------------------------------------------------------------
class Command(BaseCommand):
    help = "Convert PDFs to ChordPro format and optionally save (and tag) them in the database"

    def add_arguments(self, parser):
        parser.add_argument("input_path", type=str, help="Path to a PDF file or a folder of PDFs")
        parser.add_argument("--to-db", action="store_true", help="Save into the Song model")
        parser.add_argument("--contributor-id", type=int, help="Contributor user ID (needed with --to-db)")
        parser.add_argument(
            "--site-name",
            choices=["StrumSphere", "FrancoUke"],
            default=None,  # leave empty to hide the song
            help="Site name for imported songs (leave out to hide them)",
        )
        parser.add_argument(
            "--origin",
            default=None,
            help="Origin to set on new songs, e.g. NBU (the same value export_for_cleanup uses)",
        )
        parser.add_argument(
            "--tag",
            action="append",
            default=[],
            help="django-taggit tag to add to every song (repeat for more tags)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show the CHECK notes only; write no files and change no database rows",
        )

    def handle(self, *args, **options):
        input_path = Path(options["input_path"])
        if not input_path.exists():
            raise CommandError(f"Path does not exist: {input_path}")

        if input_path.is_file() and input_path.suffix.lower() == ".pdf":
            pdf_files = [input_path]
        elif input_path.is_dir():
            pdf_files = sorted(
                p
                for p in input_path.iterdir()
                if p.is_file() and p.suffix.lower() == ".pdf" and not p.name.startswith(".")
            )
        else:
            raise CommandError("Input must be a PDF file or a directory containing PDFs")
        if not pdf_files:
            raise CommandError("No PDF files found.")

        tags = [t.strip() for t in options["tag"] if t.strip()]
        to_db = options["to_db"] and not options["dry_run"]
        if options["to_db"] and not options.get("contributor_id"):
            raise CommandError("--contributor-id is required with --to-db")
        if tags and options["to_db"] and not hasattr(Song, TAGS_FIELD):
            raise CommandError(
                f"The Song model has no '{TAGS_FIELD}' field. Add tags = TaggableManager(blank=True) "
                "(from taggit.managers) and run makemigrations/migrate, or change TAGS_FIELD at the top of this file."
            )

        origin = resolve_origin(options["origin"]) if options["origin"] and options["to_db"] else None
        extra = {ORIGIN_FIELD: origin} if origin else {}

        created = skipped = failed = 0
        for i, pdf_file in enumerate(pdf_files, 1):
            self.stdout.write(f"[{i}/{len(pdf_files)}] Processing {pdf_file.name}...")
            try:
                title, name_date = split_title_and_date(pdf_file.stem)
                text, revised_on, warnings = pdf_to_chordpro_text(pdf_file, title, name_date)
                for w in warnings:
                    self.stdout.write(self.style.WARNING(f"    CHECK: {w}"))

                if options["dry_run"]:
                    continue

                if to_db:
                    with transaction.atomic():
                        song = Song.objects.filter(
                            songTitle=title, site_name=options["site_name"]
                        ).first()
                        if song:
                            skipped += 1
                            self.stdout.write(f"    Already in the database, not changed: {title}")
                        else:
                            song = Song.objects.create(
                                songTitle=title,
                                songChordPro=text,
                                revised_on=revised_on,
                                metadata={"source": str(pdf_file)},
                                date_posted=timezone.now(),
                                contributor_id=options["contributor_id"],
                                site_name=options["site_name"],  # can be None
                                acknowledgement=ACKNOWLEDGEMENT_TEXT,
                                **extra,
                            )
                            created += 1
                            self.stdout.write(self.style.SUCCESS(f"    Saved to DB: {song.songTitle}"))
                        if tags:
                            getattr(song, TAGS_FIELD).add(*tags)
                            self.stdout.write(f"    Tagged: {', '.join(tags)}")
                else:
                    output_path = pdf_file.with_suffix(".cho")
                    output_path.write_text(text, encoding="utf-8")
                    self.stdout.write(self.style.SUCCESS(f"    Saved file: {output_path}"))
            except Exception as e:
                failed += 1
                self.stderr.write(self.style.ERROR(f"Failed for {pdf_file}: {e}"))

        if to_db:
            self.stdout.write(
                self.style.SUCCESS(f"Done: {created} saved, {skipped} already there, {failed} failed.")
            )