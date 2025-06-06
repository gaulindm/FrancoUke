# transposer.py
from collections import Counter
import re
def detect_key(parsed_data):
    key_chords = {
        'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am'],
        'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em'],
        'Gm': ['Gm', 'Adim', 'Bb', 'Cm', 'Dm', 'Eb','F'],
        'D': ['D', 'Em', 'F#m', 'G', 'A', 'Bm'],
        'A': ['A', 'Bm', 'C#m', 'D', 'E', 'F#m'],
        'E': ['E', 'F#m', 'G#m', 'A', 'B', 'C#m'],
        'B': ['B', 'C#m', 'D#m', 'E', 'F#', 'G#m'],
        'F#': ['F#', 'G#m', 'A#m', 'B', 'C#', 'D#m'],
        'C#': ['C#', 'D#m', 'E#m', 'F#', 'G#', 'A#m'],
        'F': ['F', 'Gm', 'Am', 'Bb', 'C', 'Dm'],
        'Bb': ['Bb', 'Cm', 'Dm', 'Eb', 'F', 'Gm'],
        'Eb': ['Eb', 'Fm', 'Gm', 'Ab', 'Bb', 'Cm'],
        'Ab': ['Ab', 'Bbm', 'Cm', 'Db', 'Eb', 'Fm'],
        'Db': ['Db', 'Ebm', 'Fm', 'Gb', 'Ab', 'Bbm'],
        'Gb': ['Gb', 'Abm', 'Bbm', 'Cb', 'Db', 'Ebm'],
        'Cb': ['Cb', 'Dbm', 'Ebm', 'Fb', 'Gb', 'Abm']
    }

    chords = extract_chords(parsed_data, unique=False)
    chord_counts = Counter(chords)
    key_scores = {key: sum(chord_counts[chord] for chord in chords) for key, chords in key_chords.items()}
    detected_key = max(key_scores, key=key_scores.get)

    return detected_key

def clean_chord(chord):
    """Removes strumming indicators (slashes) from chords."""
    return re.sub(r"/+", "", chord)  # ✅ Replace one or more slashes with nothing

def extract_chords(parsed_data, unique=False):
    """Extract chords from parsed data, removing duplicates if needed."""
    chords = []
    for section in parsed_data:
        for item in section:
            if isinstance(item, dict) and 'chord' in item and item['chord']:
                clean = clean_chord(item['chord'])  # ✅ Remove slashes
                chords.append(clean)
                if clean == "[N.C.]" or clean:  # ✅ Keep [N.C.]
                    chords.append(clean)
    
    return list(set(chords)) if unique else chords  # ✅ Ensure unique chords if needed


ENHARMONIC_EQUIVALENTS = {
    "B#": "C", "E#": "F", "Cb": "B", "Fb": "E",
    "A#": "Bb", "D#": "Eb", "G#": "G#",  # ✅ Force G# notation
    "Bb": "A#", "Eb": "D#", "Ab": "G#"  # ✅ Always convert Ab → G#
}

NOTES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def normalize_chord(chord):
    """Convert enharmonic chords to a consistent sharp (#) format."""
    return ENHARMONIC_EQUIVALENTS.get(chord, chord)  # ✅ Convert flats to sharps

def transpose_chord(chord, semitones):
    """Transpose a chord by a given number of semitones, but keep [N.C.] unchanged."""
    
    #print(f"DEBUG: Received chord='{chord}'")  # 🔍 Debugging statement

    # ✅ Ensure [N.C.] is returned immediately
    if chord.strip().upper() == "[N.C.]":
        
        #print("DEBUG: Detected [N.C.], returning early")  # 🔍 Debugging statement
        return "[N.C.]"  # ✅ No processing, just return it

    root, suffix = "", ""

    # ✅ Extract root note + accidental if present
    if len(chord) > 1 and chord[1] in "#b":
        root, suffix = chord[:2], chord[2:]
    else:
        root, suffix = chord[:1], chord[1:]

    # ✅ Debug unexpected root note issue
    #print(f"DEBUG: Extracted root='{root}', suffix='{suffix}'")  # 🔍 Debugging statement

    # ✅ Ensure root is valid (fix for unexpected inputs)
    if root not in NOTES_SHARP and root not in NOTES_FLAT:
        #print(f"DEBUG: Invalid root '{root}', returning original chord")  # 🔍 Debugging statement
        return chord  # ✅ Return the original chord instead of crashing

    # ✅ Normalize root note
    if root in ENHARMONIC_EQUIVALENTS:
        root = ENHARMONIC_EQUIVALENTS[root]

    # ✅ Choose the correct scale (sharp or flat)
    notes = NOTES_SHARP if root in NOTES_SHARP else NOTES_FLAT

    # ✅ Find new transposed note
    new_index = (notes.index(root) + semitones) % 12
    transposed_root = notes[new_index]

    # ✅ Convert to standard notation
    transposed_root = normalize_chord(transposed_root)

    return transposed_root + suffix




def calculate_steps(original_key, new_key):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    original_index = notes.index(original_key)
    new_index = notes.index(new_key)
    return new_index - original_index

def transpose_lyrics(parsed_data, steps):
    transposed_data = []
    for section in parsed_data:
        transposed_section = []
        for item in section:
            if 'chord' in item and item['chord']:
                transposed_chord = transpose_chord(item['chord'], steps)
                transposed_section.append({'chord': transposed_chord, 'lyric': item['lyric']})
            else:
                transposed_section.append(item)
        transposed_data.append(transposed_section)
    return transposed_data
