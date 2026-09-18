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
        "artist": None,
        "album": None,
        "year": None,
        "songwriter": None,
        "recording": None,
    }

    html = []
    current_buffer = []
    section_type = None

    def flush_buffer():
        nonlocal current_buffer, section_type
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

            elif "lyric" in item or "chord" in item:
                chord = item.get("chord", "")
                lyric = item.get("lyric", "")  # This contains color markup tags
                
                # 🎨 Preserve color markup tags - don't escape them
                if chord:
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
                    current_buffer.append(lyric)

            # 🆕 Checked independently (not elif) — an item can carry
            # "lyric" (or "chord") AND "format" together, e.g. a chord
            # sitting at the very end of a line with no trailing lyric
            # text. Making this an elif previously meant that item's
            # LINEBREAK/PARAGRAPHBREAK was silently skipped, causing the
            # next line's lyrics to run on after it.
            if "format" in item:
                if item["format"] == "LINEBREAK":
                    current_buffer.append("<br/>")
                elif item["format"] == "PARAGRAPHBREAK":
                    flush_buffer()
                    html.append('<div class="para-break"></div>')

    flush_buffer()
    
    # 🐛 DEBUG: Print a sample to verify tags are present
    result = "".join(html)
    print("🎨 RENDERER OUTPUT (first 300 chars):")
    print(result[:300])
    print("=" * 80)
    
    return result, metadata