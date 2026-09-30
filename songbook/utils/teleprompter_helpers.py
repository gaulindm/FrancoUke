# songbook/utils/teleprompter_helpers.py
"""Helpers shared by the song teleprompter view (songbook/views.py) and the
setlist teleprompter view (setlists/views.py), so each is written only once."""
import re


# -----------------------------
# 🧠 Normalize chord names
# -----------------------------
def clean_chord_name(chord: str) -> str:
    """Normalize chord notation for consistent matching with chord library.

    Major-seventh style chords are standardized on the "maj" spelling:
    CM7, CMaj7, CΔ7 and Cmaj7 all become Cmaj7.
    """
    if not chord:
        return chord

    chord = chord.strip()

    # Remove trailing slashes (Em///)
    chord = re.sub(r"/+$", "", chord)
    # Remove bass notes like D/F#
    chord = re.sub(r"/[A-G][#b]?$", "", chord)

    # --- Normalize chord quality naming ---
    chord = re.sub(r"(?i)maj", "maj", chord)
    chord = re.sub(r"(?<=[A-G#b])M(?=\d)", "maj", chord)
    chord = chord.replace("Δ", "maj").replace("△", "maj")
    chord = re.sub(r"(?i)min", "m", chord)

    # Standardize capitalization (e.g., fm7 → Fm7)
    chord = chord.strip().replace(" ", "")
    if len(chord) > 1:
        chord = chord[0].upper() + chord[1:]
    else:
        chord = chord.upper()

    return chord


_MAJ_STYLE = re.compile(r"(?i:maj)|(?<=[A-G#b])M(?=\d)|[Δ△]")


def with_maj_aliases(chord_library):
    """Return a copy of the chord library in which every major-seventh style
    chord can be found under BOTH spellings (Cmaj7 and CM7).

    That way the songs and the library don't have to agree on the spelling
    while you convert your data, and transposing (which looks chords up by
    exact name) keeps working either way.
    """
    result = dict(chord_library)
    for key, value in chord_library.items():
        if not _MAJ_STYLE.search(key):
            continue
        canonical = clean_chord_name(key)                    # CM7   → Cmaj7
        legacy = re.sub(r"maj(?=\d)", "M", canonical)        # Cmaj7 → CM7
        result.setdefault(canonical, value)
        result.setdefault(legacy, value)
    return result


# -----------------------------
# 🎨 Color markup
# -----------------------------
def apply_html_color_markup(text):
    """
    Convert custom color tags to HTML for web display.
    Similar to PDF apply_color_markup but outputs span tags.
    """
    if not text:
        return text
    
    color_map = {
        'red': 'red',
        'blue': 'blue',
        'green': 'green',
        'yellow': 'gold',
        'orange': 'orange',
        'pink': 'hotpink',
        'purple': 'purple',
    }
    
    # Full color names: <red>text</red> → <span style='color:red'>text</span>
    for tag, color in color_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<span style='color:{color}'>{m.group(1)}</span>", text)
    
    # Short color codes: <r>text</r> → <span style='color:red'>text</span>
    short_map = {'r': 'red', 'g': 'green', 'y': 'gold'}
    for tag, color in short_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<span style='color:{color}'>{m.group(1)}</span>", text)
    
    # Custom highlight: <highlight color="blue">text</highlight>
    pattern = re.compile(r'<highlight\s+color="(.*?)">(.*?)</highlight>', re.IGNORECASE | re.DOTALL)
    text = pattern.sub(lambda m: f"<span style='background-color:{m.group(1)}'>{m.group(2)}</span>", text)
    
    # Simple highlight: <h>text</h> → yellow background
    text = re.sub(r'<h>(.*?)</h>', r"<span style='background-color:yellow'>\1</span>", text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up any nested closing tags
    text = re.sub(r'</span>\s*</span>', '</span>', text)
    
    return text
