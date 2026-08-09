import re

# Internal-use-only marker. Chosen to be something that can never appear in
# real chord text (chords are letters/digits/#/b/parentheses/slash), so it's
# safe to smuggle through the existing chord-scanning loop below.
_OPT_MARKER = "\x00OPT\x00"

# Matches <opt>[ChordName]</opt> (case-insensitive on the tag itself),
# e.g. <opt>[Em]</opt> or <OPT>[F#m7]</OPT>
_OPT_CHORD_RE = re.compile(r'<opt>\s*\[(.*?)\]\s*</opt>', re.IGNORECASE)


def _mark_optional_chords(line):
    """Replace <opt>[Chord]</chord> with [Chord<marker>] so the existing
    bracket scanner picks it up unchanged, but we can detect it was optional
    once we've extracted the chord name."""
    return _OPT_CHORD_RE.sub(lambda m: f"[{m.group(1)}{_OPT_MARKER}]", line)


def parse_song_data(chordpro_text):
    paragraphs = chordpro_text.strip().split("\n\n")
    result = []
    inside_tab_block = False
    tab_lines = []

    for p_idx, paragraph in enumerate(paragraphs):
        lines = paragraph.splitlines()
        for l_idx, line in enumerate(lines):
            stripped = line.strip()

            # TAB block start
            if stripped == "{start_of_tab}":
                inside_tab_block = True
                tab_lines = []
                continue
            if stripped == "{end_of_tab}":
                inside_tab_block = False
                result.append({"type": "tab", "lines": tab_lines})
                continue
            if inside_tab_block:
                tab_lines.append(line)
                continue

            # 🎯 NEW: Handle {instruction: ...}
            if stripped.lower().startswith("{instruction:"):
                # Extract everything between {instruction: and }
                instruction_text = stripped[len("{instruction:"):-1].strip()
                if instruction_text:
                    result.append([{"instruction": instruction_text}])
                continue

            # 🎯 Existing: Directives like {soc}, {sov}, {title: ...}, etc.
            directive_match = re.match(r'{(.*?)\s*:?([^}]*)}', stripped)
            if directive_match:
                directive_str = stripped
                result.append([{"directive": directive_str}])
                continue

            # 🎯 Lyrics/chords parsing
            # Pre-process <opt>[Chord]</opt> -> [Chord<marker>] so the
            # bracket scanner below handles it like any other chord, and we
            # can flag it as optional once extracted.
            line = _mark_optional_chords(line)

            i = 0
            buffer = ""
            group = []
            while i < len(line):
                if line[i] == "[":
                    end = line.find("]", i)
                    if end != -1:
                        chord = line[i+1:end]
                        is_optional = chord.endswith(_OPT_MARKER)
                        if is_optional:
                            chord = chord[:-len(_OPT_MARKER)]
                        if buffer:
                            group.append({"lyric": buffer})
                            buffer = ""
                        chord_item = {"chord": chord, "lyric": ""}
                        if is_optional:
                            chord_item["optional"] = True
                        group.append(chord_item)
                        i = end + 1
                    else:
                        i += 1
                else:
                    if group and "chord" in group[-1] and group[-1]["lyric"] == "":
                        group[-1]["lyric"] += line[i]
                    else:
                        buffer += line[i]
                    i += 1

            if buffer:
                group.append({"lyric": buffer})
            if group:
                # 🧱 Inject LINEBREAK if not last line in paragraph
                if l_idx < len(lines) - 1:
                    group.append({"format": "LINEBREAK"})
                result.append(group)

        # 🔲 Inject PARAGRAPHBREAK if not last paragraph
        if p_idx < len(paragraphs) - 1:
            result.append([{"format": "PARAGRAPHBREAK"}])

    return result