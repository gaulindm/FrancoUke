def render_lyrics_with_chords_html(lyrics_with_chords, site_name="StrumSphere"):
    """
    Render parsed lyrics_with_chords (list of groups) into HTML,
    while extracting metadata directives (title, artist, year, etc.).
    """

    directive_map = {
        "FrancoUke": {
            "{soi}": "Intro", "{soc}": "Refrain", "{sov}": "Couplet",
            "{sob}": "Pont", "{soo}": "Outro", "{sod}": "Interlude",
            "{eoi}": None, "{eoc}": None, "{eov}": None,
            "{eob}": None, "{eoo}": None, "{eod}": None
        },
        "StrumSphere": {
            "{soi}": "Intro", "{soc}": "Chorus", "{sov}": "Verse",
            "{sob}": "Bridge", "{soo}": "Outro", "{sod}": "Interlude",
            "{eoi}": None, "{eoc}": None, "{eov}": None,
            "{eob}": None, "{eoo}": None, "{eod}": None
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
            if section_type and section_type.lower() != "verse":
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

            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]
                if chord:
                    current_buffer.append(f"<b>[{chord}]</b>{lyric}")
                else:
                    current_buffer.append(lyric)

            elif "format" in item:
                if item["format"] == "LINEBREAK":
                    current_buffer.append("<br/>")
                elif item["format"] == "PARAGRAPHBREAK":
                    flush_buffer()
                    html.append('<div class="para-break"></div>')

    flush_buffer()
    return "".join(html), metadata
