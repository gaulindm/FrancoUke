import re

from songbook.utils.transposer import transpose_chordpro


# Regex to match chords like [C], [C#m7], [Bbadd9], etc.
CHORD_REGEX = re.compile(r"\[([A-G][#b]?(?:m|maj|min|dim|aug|sus|add)?\d*(?:\([^\)]*\))?[^\]]*)\]")

# Map sharp names to preferred equivalents
ENHARMONIC_MAP = {
    "D#": "Eb",
    "G#": "Ab",
    "A#": "Bb",
    # Optional: remove oddballs pychord might emit
    "E#": "F",
    "B#": "C",
    "Cb": "B",
    "Fb": "E",
}

def normalize_chord_string(chord_str: str) -> str:
    # Replace root note only (e.g., A#, G#) with preferred version
    for sharp, preferred in ENHARMONIC_MAP.items():
        if chord_str.startswith(sharp):
            return chord_str.replace(sharp, preferred, 1)
    return chord_str


def transpose_chordpro_text(text: str, semitones: int) -> str:
    if not text:
        return text
    print("Transposing in admin using transposer.py!")
    return transpose_chordpro(text, semitones)
