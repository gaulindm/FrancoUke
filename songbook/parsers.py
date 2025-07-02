import re

def parse_song_data(data):
    song_parts = []
    current_part = []

    # Split the data into lines
    lines = data.split('\n')
    
    previous_blank = False  # Track consecutive blank lines for paragraph breaks

    for line in lines:
        line = line.strip()

        if not line:  # Blank line
            if current_part:
                if previous_blank:  # Consecutive blank lines indicate paragraph break
                    current_part.append({"format": "PARAGRAPHBREAK"})
                    previous_blank = False  # Reset after marking paragraph
                else:
                    current_part.append({"format": "LINEBREAK"})
                    previous_blank = True  # Mark as first blank line
            continue

        previous_blank = False  # Reset blank line tracking when a new line starts

        if line.startswith('{'):  # Directive line
            if current_part:
                song_parts.append(current_part)
            current_part = [{"directive": line}]
        else:  # Chord/lyric line or lyric-only line
            # Split the line into parts based on chords
            parts = re.split(r"(\[[^\]]+\])", line)
            parts = [part for part in parts if part]  # Remove empty parts

            for i, part in enumerate(parts):
                if part.startswith("["):  # Chord
                    # Get the corresponding lyric
                    prev = parts[i - 1].rstrip() if i > 0 else ""
                    lyric = parts[i + 1].lstrip() if i + 1 < len(parts) else ""
                    current_part.append({"chord": part[1:-1].strip(), "lyric": lyric})

                elif i == 0 or not parts[i - 1].startswith("["):  # Intro text or lyric without preceding chord
                    current_part.append({"chord": "", "lyric": part.strip()})

            current_part.append({"format": "LINEBREAK"})  # Add LINEBREAK at the end

    if current_part:
        song_parts.append(current_part)

    return song_parts

import re

def parse_chordpro_text(chordpro_text):
    lines = chordpro_text.splitlines()
    result = []
    metadata = {}
    inside_tab_block = False
    tab_lines = []

    for line in lines:
        stripped = line.strip()

        # Handle metadata like {title: Hello}
        meta_match = re.match(r'{(.*?):\s*(.*)}', stripped)
        if meta_match and not inside_tab_block:
            key, value = meta_match.groups()
            metadata[key.lower()] = value
            continue

        # TAB BLOCK START
        if stripped == '{start_of_tab}':
            inside_tab_block = True
            tab_lines = []
            continue

        # TAB BLOCK END
        if stripped == '{end_of_tab}':
            inside_tab_block = False
            result.append({
                "type": "tab",
                "lines": tab_lines
            })
            continue

        # Inside a tab block
        if inside_tab_block:
            tab_lines.append(line)
            continue

        # Handle regular chord/lyric lines
        chord_line = ""
        lyric_line = ""
        i = 0

        while i < len(line):
            if line[i] == '[':
                end = line.find(']', i)
                if end != -1:
                    chord = line[i+1:end]
                    chord_line += chord.ljust(end - i)
                    lyric_line += ' ' * (end - i + 1)
                    i = end + 1
                else:
                    # malformed chord - skip
                    i += 1
            else:
                chord_line += ' '
                lyric_line += line[i]
                i += 1

        if line.strip():
            result.append({
                "type": "lyrics_with_chords",
                "chords": chord_line.rstrip(),
                "lyrics": lyric_line.rstrip()
            })

    return metadata, result
