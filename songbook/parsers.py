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

# Example usage:
# data = "your song text here"
# parsed_data = parse_song_data(data)
# print(parsed_data)
