import re

# Tags where the value is simply "everything up to the closing brace"
SIMPLE_TAGS = [
    "artist", "songwriter", "capo", "album", "key", "1stnote", "tempo",
    "timeSignature", "strumming", "x_strumming", "count_in",
    "short_instruction_1", "short_instruction_2", "suggested_alternate",
    "adapted_from", "subtitle", "youtube",
]


def _find(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
    return m.group(1).strip() if m else None


def parse_metadata(chordpro):
    """Return (title, metadata_dict) from the {tag: value} lines of a ChordPro text."""
    title = _find(r'{(?:title|t):\s*([^\}]+)}', chordpro) or "Untitled Song"
    metadata = {"comment": _find(r'{(?:comment|c):\s*(.+?)}', chordpro)}
    metadata["year"] = _find(r'{year:\s*(\d{4})}', chordpro)
    for tag in SIMPLE_TAGS:
        metadata[tag] = _find(rf'{{{tag}:\s*(.+?)}}', chordpro)
    return title, metadata