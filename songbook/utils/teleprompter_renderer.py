import logging
import re

logger = logging.getLogger(__name__)


def render_lyrics_with_chords_html(lyrics_with_chords, site_name="StrumSphere", chord_position="inline"):
    """
    Render parsed lyrics_with_chords (list of groups) into HTML,
    while extracting metadata directives (title, artist, year, etc.).
    Preserves color markup tags like <r>, <g>, <y>, <b>, <i>, <u>, etc.

    chord_position:
        "inline" (default) - existing behavior, chord name printed in the
            reading line itself, e.g. "[C] sunshine"
        "above" - chord name is placed in a positioned span above the
            lyric fragment (via CSS), for beginner-friendly ChordPro-style
            display: no brackets in the reading line.
    """

    directive_map = {
        "FrancoUke": {
            "{soi}": "Intro", "{soc}": "Refrain", "{sov}": "Couplet",
            "{sob}": "Pont", "{soo}": "Outro", "{sod}": "Interlude",
            "{sos}": "",
            "{eoi}": None, "{eoc}": None, "{eov}": None,
            "{eob}": None, "{eoo}": None, "{eod}": None,
            "{eos}": None  # 🆕 Add this
        },
        "StrumSphere": {
            "{soi}": "Intro", "{soc}": "Chorus", "{sov}": "Verse",
            "{sob}": "Bridge", "{soo}": "Outro", "{sod}": "Interlude",
            "{sos}": "",
            "{eoi}": None, "{eoc}": None, "{eov}": None,
            "{eob}": None, "{eoo}": None, "{eod}": None,
            "{eos}": None  # 🆕 Add this
        }
    }
    selected_map = directive_map.get(site_name, directive_map["StrumSphere"])

    metadata = {
        "title": None,
        "subtitle": None,
        "artist": None,
        "album": None,
        "year": None,
        "songwriter": None,
        "recording": None,
    }

    html = []
    current_buffer = []
    section_type = None

    # 🆕 Singing-group markers: {c:1}, {c:2}, {c:1+2}, {c:All}.
    # A marker applies ONLY to the single line right after it. We remember
    # it in pending_group until that line's first chord/lyric arrives, wrap
    # the line in <div class="grp grp-N">, and close it at the LINEBREAK.
    # Accepts {c:1}, {c:VG1}, {c:VG 2}, {c:1+2}, {c:All}. The optional "VG"
    # prefix is dropped, so VG1 and 1 produce the same colour class.
    GROUP_RE = re.compile(
        r'^\s*(?:vg\s*)?(\d+(?:\s*[+&,]\s*\d+)*|all|tous|tutti)\s*$', re.I
    )
    # 🔧 TUNE: text shown in the badge for numbered groups ({n} = 1, 2, 1+2).
    # Use "VG{n}" for a shorter badge, e.g. on a projector with big text.
    VOCAL_GROUP_LABEL = "Vocal Group {n}"
    # 🆕 Hold cue: {c:(23)} at the end of a line = keep strumming the last
    # chord through those beats (2 and 3). Rendered inline, in orange.
    HOLD_RE = re.compile(r'^\s*\(\s*([\d,\s]+?)\s*\)\s*$')
    # The parser leaves {c:(...)} as plain lyric text when it sits at the
    # END of a line, so also catch it inside lyric strings.
    HOLD_INLINE_RE = re.compile(r'\s*\{c:\s*\(\s*([\d,\s]+?)\s*\)\s*\}', re.I)

    def inline_holds(lyric):
        return HOLD_INLINE_RE.sub(
            lambda m: f'<span class="hold-cue">({m.group(1).replace(" ", "")})</span>',
            lyric,
        )
    pending_group = None   # marker waiting for the next line of lyrics
    open_group = False     # currently inside a group line?

    def close_group():
        nonlocal open_group
        if open_group:
            current_buffer.append('</div>')
            open_group = False

    def start_group_line():
        nonlocal pending_group, open_group
        if pending_group and not open_group:
            label = pending_group
            cls = 'grp-' + re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')
            # Numbered groups read "Vocal Group 1"; All/Tous/Tutti stay as written.
            shown = (
                VOCAL_GROUP_LABEL.format(n=label.replace(" ", ""))
                if label[0].isdigit() else label
            )
            current_buffer.append(
                f'<div class="grp {cls}">'
                f'<span class="grp-badge">{shown}</span>'
            )
            open_group = True
            pending_group = None

    def flush_buffer():
        nonlocal current_buffer, section_type
        close_group()
        if current_buffer:
            text = "".join(current_buffer)
            # 🆕 Check for empty section_type (centered sections with no label)
            if section_type == "":
                html.append(f'<div class="centered">{text}</div>')
            elif section_type and section_type.lower() != "verse":
                html.append(
                    f'<div class="section">'
                    f'<div class="section-name">{section_type}</div>'
                    f'<div class="section-body">{text}</div>'
                    f'</div>'
                )
            else:
                html.append(f'<div class="verse">{text}</div>')
            current_buffer = []

    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                directive = item["directive"]
                key_val = directive.strip("{}").split(":", 1)
                key = key_val[0].strip().lower()
                val = key_val[1].strip() if len(key_val) > 1 else ""

                # Metadata
                if key in ["t", "title"]:
                    metadata["title"] = val
                elif key in ["st", "subtitle"]:
                    metadata["subtitle"] = val
                elif key == "artist":
                    metadata["artist"] = val
                elif key == "album":
                    metadata["album"] = val
                elif key == "year":
                    metadata["year"] = val
                elif key == "songwriter":
                    metadata["songwriter"] = val
                elif key == "recording":
                    metadata["recording"] = val

                # Section markers
                elif directive in selected_map:
                    flush_buffer()
                    section_type = selected_map[directive]

            # 🆕 {c:...} / {comment:...} — flush whatever's buffered so the
            # comment renders as its own standalone block, then keep going
            # with the same section_type (a comment is an aside, not a
            # section boundary).
            elif "comment" in item:
                text = item["comment"].strip()
                hold = HOLD_RE.match(text)
                if hold:
                    # 🆕 Hold cue: stays on the current line. No flush and
                    # no `continue`, so a LINEBREAK attached to this item
                    # still gets handled by the `format` check below.
                    current_buffer.append(
                        f'<span class="hold-cue">({hold.group(1)})</span>'
                    )
                elif GROUP_RE.match(text):
                    # 🆕 Singing-group marker: don't render it on its own;
                    # it decorates the next line. `continue` also skips any
                    # LINEBREAK attached to the marker item itself.
                    pending_group = GROUP_RE.match(text).group(1).strip()
                    continue
                else:
                    flush_buffer()
                    html.append(f'<div class="song-comment">{item["comment"]}</div>')

            elif "lyric" in item or "chord" in item:
                chord = item.get("chord", "")
                lyric = inline_holds(item.get("lyric", ""))  # color markup tags kept
                
                # 🎨 Preserve color markup tags - don't escape them
                if chord:
                    start_group_line()
                    if chord_position == "above":
                        current_buffer.append(
                            f'<span class="chord-word">'
                            f'<span class="chord-label" data-chord="{chord}">{chord}</span>'
                            f'{lyric}</span>'
                        )
                    else:
                        current_buffer.append(
                            f'<b class="chord-token" data-chord="{chord}">[{chord}]</b>{lyric}'
                        )
                elif lyric.strip() == "" and lyric != "":
                    # 🆕 Blank-line divider convention: an item with no chord
                    # whose lyric is ONLY whitespace (e.g. a single space)
                    # exists purely to pair with the following LINEBREAK and
                    # create a blank line — it isn't real text. Emitting the
                    # literal space character here caused browsers to render
                    # it as a stray leading space on the next line (visible
                    # as an unwanted indent). Skip it; the LINEBREAK item
                    # still fires normally and produces the blank line.
                    pass
                else:
                    start_group_line()
                    current_buffer.append(lyric)

            # 🆕 Checked independently (not elif) — an item can carry
            # "lyric" (or "chord") AND "format" together, e.g. a chord
            # sitting at the very end of a line with no trailing lyric
            # text. Making this an elif previously meant that item's
            # LINEBREAK/PARAGRAPHBREAK was silently skipped, causing the
            # next line's lyrics to run on after it.
            if "format" in item:
                if item["format"] == "LINEBREAK":
                    if open_group:
                        close_group()   # the block ends the line: no <br/>
                    elif pending_group:
                        pass            # this break belongs to the marker line
                    else:
                        current_buffer.append("<br/>")
                elif item["format"] == "PARAGRAPHBREAK":
                    pending_group = None
                    flush_buffer()
                    html.append('<div class="para-break"></div>')

    flush_buffer()
    
    result = "".join(html)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Renderer output (first 300 chars): %s", result[:300])

    return result, metadata