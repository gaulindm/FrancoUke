import re

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

            # Directives like {title: ...}
            directive_match = re.match(r'{(.*?)\s*:?([^}]*)}', stripped)
            if directive_match:
                directive_str = stripped
                result.append([{"directive": directive_str}])
                continue

            # Lyrics/chords parsing
            i = 0
            buffer = ""
            group = []
            while i < len(line):
                if line[i] == "[":
                    end = line.find("]", i)
                    if end != -1:
                        chord = line[i+1:end]
                        if buffer:
                            group.append({"lyric": buffer})
                            buffer = ""
                        group.append({"chord": chord, "lyric": ""})
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
