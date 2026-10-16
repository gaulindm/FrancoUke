import re

SUFFIX_ALIASES = {
    '+': 'aug',  '+7': 'aug7',  '7+': 'aug7',  '#5': 'aug',  '7#5': 'aug7',
    'o': 'dim',  '°': 'dim',  '˚': 'dim',  'º': 'dim',
    'o7': 'dim7', '°7': 'dim7', '˚7': 'dim7', 'º7': 'dim7',
    'ø': 'm7b5', 'ø7': 'm7b5', 'm7-5': 'm7b5', 'm7(b5)': 'm7b5',
    '-': 'm', '-6': 'm6', '-7': 'm7', '-9': 'm9',
    'sus': 'sus4',
    'M': '',            # CM / Cmaj = plain C major
    'm(M7)': 'mM7',
}

# ------------------------------------------------------------
# Helper: normalize maj/min tokens
# ------------------------------------------------------------

def normalize_maj_tokens(name: str) -> str:
    name = re.sub(r'(?i)maj', 'M', name)
    name = re.sub(r'(?i)Δ', 'M', name)
    name = re.sub(r'(?i)min', 'm', name)

    m = re.match(r'^([A-Ga-g][#b♭]?)(.*)$', name)
    if not m:
        return name
    root, suffix = m.groups()
    return root + SUFFIX_ALIASES.get(suffix, suffix)

# ------------------------------------------------------------
# Helper: canonicalize enharmonic root
# ------------------------------------------------------------
ENHARMONIC_TO_SHARP = {
    'CB': 'B',
    'DB': 'C#',
    'EB': 'D#',
    'GB': 'F#',
    'AB': 'G#',
    'BB': 'A#',
    'FB': 'E',
    'C#': 'C#', 'D#': 'D#', 'F#': 'F#', 'G#': 'G#', 'A#': 'A#',
}

def canonicalize_enharmonic(chord_name: str) -> str:
    chord_name = chord_name.strip()
    m = re.match(r'^([A-Ga-g])([#b♭]?)(.*)$', chord_name)
    if not m:
        return chord_name

    root_letter = m.group(1).upper()
    accidental = m.group(2).replace('♭', 'b')
    rest = m.group(3) or ''

    root = root_letter + accidental
    root_key = root.upper()

    if root_key in ENHARMONIC_TO_SHARP:
        root_canonical = ENHARMONIC_TO_SHARP[root_key]
    else:
        root_canonical = root_letter + accidental

    return f"{root_canonical}{rest}"


# ------------------------------------------------------------
# Helper: extract just the root (letter + accidental) from a
# canonicalized chord name, so we can confirm two chords share
# the same root before treating them as naming-convention
# equivalents (e.g. "Cdim" vs "Cdim7").
# ------------------------------------------------------------
def extract_root(chord_name: str):
    m = re.match(r'^([A-G][#b]?)', chord_name)
    return m.group(1) if m else None


# ------------------------------------------------------------
# Main comparison function
# ------------------------------------------------------------
def chord_equivalent(a: str, b: str) -> bool:
    if not a or not b:
        return False

    # strip trailing slashes
    a = re.sub(r'/+$', '', a.strip())
    b = re.sub(r'/+$', '', b.strip())

    # remove /bass notes
    a = re.sub(r'/[A-G][#b]?$', '', a)
    b = re.sub(r'/[A-G][#b]?$', '', b)

    # maj/min cleanup
    a = normalize_maj_tokens(a)
    b = normalize_maj_tokens(b)

    # canonicalize enharmonic roots
    a_can = canonicalize_enharmonic(a)
    b_can = canonicalize_enharmonic(b)

    # quick match
    if a_can == b_can:
        return True

    # NOTE: dim and dim7 are intentionally NOT treated as equivalent here.
    # They are musically distinct chords (diminished triad vs diminished
    # seventh), not alternate spellings of the same chord. A previous
    # version of this function special-cased "same root + dim/dim7" as
    # equivalent, which incorrectly collapsed chords like D#dim7 and Ebdim
    # into a single entry.

    return a_can == b_can