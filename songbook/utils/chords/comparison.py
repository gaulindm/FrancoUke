import re

# ------------------------------------------------------------
# Helper: normalize maj/min tokens
# ------------------------------------------------------------
def normalize_maj_tokens(name: str) -> str:
    name = re.sub(r'(?i)maj', 'M', name)
    name = re.sub(r'(?i)Δ', 'M', name)
    name = re.sub(r'(?i)min', 'm', name)
    return name

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

    # dim vs dim7
    if re.match(r'^[A-G][#]?[dD]im$', a_can) and re.match(r'^[A-G][#]?[dD]im7$', b_can):
        return True
    if re.match(r'^[A-G][#]?[dD]im7$', a_can) and re.match(r'^[A-G][#]?[dD]im$', b_can):
        return True

    return a_can == b_can
