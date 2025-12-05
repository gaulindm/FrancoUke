# loader.py
import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from django.conf import settings
from songbook.utils.transposer import normalize_chord, clean_chord, transpose_chord
from songbook.utils.chords.comparison import chord_equivalent
from songbook.utils.chords.normalize import normalize_variation


logger = logging.getLogger(__name__)

# -----------------------
# Chord JSON directory
# -----------------------
CHORDS_DIR: Path = Path(settings.BASE_DIR) / "songbook" / "chords"


# songbook/utils/chords/loader.py
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from django.conf import settings
#from .normalize import normalize_chord  # canonical normalize function

logger = logging.getLogger(__name__)

# Path to chord JSON files
CHORDS_DIR: Path = Path(settings.BASE_DIR) / "songbook" / "chords"

def load_chords(instrument: str) -> List[Dict[str, Any]]:
    """
    Load chord definitions for a specific instrument.
    Adds common aliases such as "Cmaj7" -> "CM7".
    
    Args:
        instrument: Instrument type (ukulele, guitar, etc.)
    
    Returns:
        List of chord definition dictionaries, each with an "instrument" field.
    """
    file_path: Path = CHORDS_DIR / f"{instrument}.json"

    if not file_path.exists():
        logger.error("Chord file not found for %s at %s", instrument, file_path)
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            chords = json.load(f)

        extended_chords: List[Dict[str, Any]] = []

        for chord in chords:
            # Copy original chord dict and add instrument info
            chord_copy = dict(chord)
            chord_copy["instrument"] = instrument
            extended_chords.append(chord_copy)

            # Add alias: Cmaj7 -> CM7
            chord_name = chord_copy.get("name", "")
            if chord_name.endswith("maj7"):
                alias_chord = dict(chord_copy)
                alias_chord["name"] = chord_name.replace("maj7", "M7")
                extended_chords.append(alias_chord)

        added_aliases = len(extended_chords) - len(chords)
        logger.debug("Loaded %d chords for %s (%d aliases added)",
                     len(chords), instrument, added_aliases)

        return extended_chords

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", file_path, e)
        return []




def extract_used_chords(lyrics_with_chords: Any) -> list[str]:
    """
    Extract chord names from a nested JSON-like structure.
    Returns a sorted list of unique chord names.
    """
    chords = set()

    def traverse_structure(data: Any):
        if isinstance(data, dict):
            if "chord" in data and data["chord"]:
                chords.add(data["chord"])
            for value in data.values():
                traverse_structure(value)
        elif isinstance(data, list):
            for item in data:
                traverse_structure(item)

    traverse_structure(lyrics_with_chords)
    return sorted(chords)

# =======================
# LOAD RELEVANT CHORDS
# =======================
def load_relevant_chords(songs, user_prefs, transpose_value):
    """
    Load chords for the primary instrument ONLY, including requested alternates
    from chordpro syntax such as [C(1)], and optionally showing default alternates
    based on user preference.

    Rules:
    - Always include primary variation (v0).
    - If chordpro requests a variation N via [C(N)], ALWAYS include it.
    - If user preference for alternates is ON, include v1 unless overridden.
    - If chordpro requests (0), then DO NOT auto-include alternates.
    """

    import re

    # ------------------------------------------------------------
    # Helper: parse chordpro forced variation, e.g. "C(1)" -> ("C", 1)
    # ------------------------------------------------------------
    def parse_requested_variation(chord_name: str):
        match = re.match(r"^([A-G][#b]?m?(?:add\d+)?)(?:\((\d+)\))?$", chord_name)
        if not match:
            return chord_name, None

        base = match.group(1)
        forced = match.group(2)
        forced_idx = int(forced) if forced is not None else None
        return base, forced_idx

    # ------------------------------------------------------------
    # Helper: choose which variations to include
    # ------------------------------------------------------------
    def select_variations(base_name, all_variations, user_pref_show_alt, requested_dict):
        result = []

        # Always include v0
        if len(all_variations) > 0:
            result.append(all_variations[0])

        forced = requested_dict.get(base_name, None)

        # SONG FORCES A VARIATION
        if forced is not None:
            if forced < len(all_variations) and forced != 0:
                result.append(all_variations[forced])
            return result

        # USER PREF: INCLUDE DEFAULT ALTERNATE v1
        if user_pref_show_alt and len(all_variations) > 1:
            result.append(all_variations[1])

        return result

    # ------------------------------------------------------------
    # Load primary instrument dictionary
    # ------------------------------------------------------------
    primary_inst = user_prefs.get("primary_instrument") or "ukulele"
    show_alternates = user_prefs.get("show_alternate_chords", False)

    chords_primary = load_chords(primary_inst)

    for c in chords_primary:
        c["instrument"] = primary_inst

    # ------------------------------------------------------------
    # Extract raw chords from the song
    # ------------------------------------------------------------
    raw_used = extract_used_chords(songs[0].lyrics_with_chords)

    # MAP: {base_name -> forced_variation_index}
    requested_variations = {}

    # Build request map FIRST so transposed chords keep correct overrides
    for ch in raw_used:
        cleaned = normalize_chord(clean_chord(ch))
        base, forced = parse_requested_variation(cleaned)
        if forced is not None:
            requested_variations[base] = forced

    # ------------------------------------------------------------
    # Normalize + transpose the chords
    # ------------------------------------------------------------
    used_cleaned = [normalize_chord(clean_chord(ch)).strip() for ch in raw_used]
    transposed_chords = {
        transpose_chord(clean_chord(ch).strip(), transpose_value).strip()
        for ch in used_cleaned
    }

    # ------------------------------------------------------------
    # Build final relevant chord list
    # ------------------------------------------------------------
    relevant_chords = []
    added_keys = set()

    for t_chord in transposed_chords:
        if not t_chord:
            continue

        # Extract base name again AFTER transposition
        base, _ = parse_requested_variation(t_chord)

        for chord_def in chords_primary:
            if chord_equivalent(chord_def.get("name", ""), base):
                key = (chord_def.get("name", "").lower(), primary_inst)
                if key in added_keys:
                    break

                # Copy and override variations intelligently
                chord_copy = dict(chord_def)

                # Pick the correct variations (forced > user preference > default v0)
                chord_copy["variations"] = select_variations(
                    base,
                    chord_def.get("variations", []),
                    show_alternates,
                    requested_variations
                )

                chord_copy["requested_name"] = base
                chord_copy["instrument"] = primary_inst

                relevant_chords.append(chord_copy)
                added_keys.add(key)
                break

    return relevant_chords

