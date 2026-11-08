# songbook/utils/abc_riffs.py
"""Finds the ABC melody blocks ("riffs") written inside a song's ChordPro text:

    {start_of_abc: Intro riff}
    M:4/4
    L:1/8
    K:C
    E2 G2 c2 B2 | A2 G2 E4 |]
    {end_of_abc}
"""
import re

_START = re.compile(r'^\s*\{\s*start_of_abc\s*(?::\s*(.*?))?\s*\}\s*$', re.IGNORECASE)
_END = re.compile(r'^\s*\{\s*end_of_abc\s*\}\s*$', re.IGNORECASE)
_TEMPO = re.compile(r'^\s*\{\s*tempo\s*:\s*(\d+)', re.IGNORECASE | re.MULTILINE)


def has_riffs(chordpro_text):
    """Quick yes/no, without splitting the text."""
    return bool(chordpro_text) and bool(re.search(r'\{\s*start_of_abc\b', chordpro_text, re.IGNORECASE))


def extract_riffs(chordpro_text):
    """Return a list of {"label", "abc", "tempo"} dicts, one per ABC block in the song.

    "tempo" is the song's {tempo: N} value (or None); it is used when the riff has no Q: line.
    """
    if not has_riffs(chordpro_text):
        return []
    tempo_match = _TEMPO.search(chordpro_text)
    tempo = int(tempo_match.group(1)) if tempo_match else None

    riffs, inside, label, lines = [], False, "", []
    for line in chordpro_text.splitlines():
        if not inside:
            start = _START.match(line)
            if start:
                inside, label, lines = True, (start.group(1) or "").strip(), []
        elif _END.match(line):
            abc = "\n".join(lines).strip()
            if abc:
                riffs.append({"label": label, "abc": abc, "tempo": tempo})
            inside = False
        else:
            lines.append(line.rstrip())
    return riffs