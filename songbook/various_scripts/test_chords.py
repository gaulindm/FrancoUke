import re

# === Fixed and verified regex ===
CHORD_REGEX = re.compile(
    r"\[("
    r"[A-G][#b]?"                            # Root
    r"(?:m(?!aj)|M|maj|min|dim|aug|sus|add)?" # Quality
    r"[0-9]*"                                # Extension (7, 9, etc.)
    r"(?:/[A-G][#b]?)?"                      # Slash chord
    r"/*"                                    # Strumming slashes
    r")\]"
)

def clean_chord(chord):
    """
    Removes trailing strumming indicators like Em/// → Em
    but preserves real slash chords like D/F# or CM7/E.
    """
    if re.match(r"^[A-G][#b]?(?:m(?!aj)|M|maj|min|dim|aug|sus|add)?[0-9]*/[A-G][#b]?$", chord):
        return chord
    return re.sub(r"/+$", "", chord)

# === Test ===
test_text = "[Em///] [D/F#] [C] [CM7] [Cm7] [Am///] [Cmaj7/E]"
matches = CHORD_REGEX.findall(test_text)
print("🎸 Detected chords:", matches)
print("🧹 Cleaned chords:", [clean_chord(c) for c in matches])
