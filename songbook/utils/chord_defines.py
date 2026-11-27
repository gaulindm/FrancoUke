"""
Per-song chord diagrams from ChordPro {define:} directives.

Example lines inside a song:
    {define: F/G frets 0 0 1 0}
    {define: Bb base-fret 3 frets 0 1 1 1}

Ukulele strings are G C E A. Use x for a muted string. With base-fret, the
fret numbers are relative to it (1 = the base fret itself), as in ChordPro.

The result is {chord_name: {"positions": [...], "baseFret": int}}, the same
shape normalize_variation() in chord_diagram_svg.py and drawChordDiagram()
in chord_diagrams.js already understand.
"""
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)

DEFINE_RE = re.compile(
    r'^\s*\{\s*define\s*:\s*(.+?)\s*\}\s*$',
    re.IGNORECASE | re.MULTILINE,
)
KEYWORDS = {"base-fret", "frets", "fingers", "copy", "display", "diagram"}


def _fret_value(token: str) -> int:
    t = token.strip().lower()
    if t in ("x", "n", "-", "-1"):
        return -1          # muted -> drawn as X where markers are shown
    return int(t)


def parse_define_directives(chordpro_text: str) -> Dict[str, Dict[str, Any]]:
    """Return {chord_name: variation_dict} for every {define:} found.

    Accepts a whole song or a single "{define: ...}" string. A badly written
    define is skipped (and logged) instead of breaking the page.
    """
    custom: Dict[str, Dict[str, Any]] = {}
    for match in DEFINE_RE.finditer(chordpro_text or ""):
        try:
            tokens = match.group(1).split()
            if not tokens:
                continue
            name, rest = tokens[0], tokens[1:]

            base_fret = None
            frets = []
            i = 0
            while i < len(rest):
                word = rest[i].lower()
                if word == "base-fret" and i + 1 < len(rest):
                    base_fret = int(rest[i + 1])
                    i += 2
                elif word == "frets":
                    i += 1
                    while i < len(rest) and rest[i].lower() not in KEYWORDS:
                        frets.append(_fret_value(rest[i]))
                        i += 1
                elif word in KEYWORDS:      # fingers, copy, ... -> skip their values
                    i += 1
                    while i < len(rest) and rest[i].lower() not in KEYWORDS:
                        i += 1
                else:
                    i += 1

            if not frets:
                continue

            variation: Dict[str, Any] = {"positions": frets, "baseFret": 1}
            if base_fret and base_fret > 1:
                # ChordPro frets are relative to base-fret; the renderers use absolute
                variation["positions"] = [
                    f + base_fret - 1 if f > 0 else f for f in frets
                ]
                variation["baseFret"] = base_fret
            custom[name] = variation
        except ValueError:
            logger.warning("Ignoring bad {define:} line: %s", match.group(0).strip())
    return custom