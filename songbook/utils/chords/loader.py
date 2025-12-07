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
def load_relevant_chords(songs, user_prefs, transpose_value, suggested_alternate=None):
    """
    Load chords for the primary instrument ONLY, including requested alternates
    from chordpro syntax such as [C(1)], and optionally showing default alternates
    based on user preference.

    Rules:
    - Always include primary variation (v0).
    - If chordpro requests a variation N via [C(N)], ALWAYS include it.
    - If suggested_alternate is specified, ALWAYS include that variation.
    - If user preference for alternates is ON, include v1 unless overridden.
    """

    import re

    # 🐛 DEBUG
    print("=" * 60)
    print("LOAD_RELEVANT_CHORDS DEBUG:")
    print(f"  suggested_alternate input: {suggested_alternate}")
    print(f"  show_alternate_chords pref: {user_prefs.get('show_alternate_chords', False)}")
    print("=" * 60)

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

        forced_list = requested_dict.get(base_name, None)

        # 🐛 DEBUG
        print(f"  select_variations for '{base_name}':")
        print(f"    - total variations available: {len(all_variations)}")
        print(f"    - forced variations from requested_dict: {forced_list}")
        print(f"    - user_pref_show_alt: {user_pref_show_alt}")

        # SONG FORCES VARIATION(S) (from suggested_alternate OR inline [C(1)])
        if forced_list is not None:
            print(f"    - FORCED variations detected: {forced_list}")
            for forced in forced_list:
                if forced < len(all_variations) and forced != 0:
                    if all_variations[forced] not in result:
                        result.append(all_variations[forced])
                        print(f"    - Added variation {forced}")
                    else:
                        print(f"    - Variation {forced} already in result (skipped)")
                else:
                    print(f"    - Forced variation {forced} is invalid or is 0")
            
            # 🐛 NEW DEBUG: Show what's actually in result
            print(f"    - Result list has {len(result)} items:")
            for idx, var in enumerate(result):
                print(f"      [{idx}] = {var}")
            
            print(f"    - Final variations: {len(result)} variations")
            return result

        # USER PREF: INCLUDE DEFAULT ALTERNATE v1
        if user_pref_show_alt:
            for idx in range(1, len(all_variations)):
                if all_variations[idx] not in result:
                    result.append(all_variations[idx])
                    print(f"    - Added v{idx} due to user preference")

        print(f"    - Final variations: {len(result)} variations")
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
    
    # 🐛 DEBUG
    print(f"Raw chords extracted: {raw_used}")

    # MAP: {base_name -> LIST of forced_variation_indices}
    requested_variations = {}

    # 🆕 Process suggested_alternate from metadata FIRST (global override)
    if suggested_alternate:
        print(f"Processing suggested_alternate: '{suggested_alternate}'")
        # Split by comma to support multiple alternates
        alternates = [alt.strip() for alt in suggested_alternate.split(',')]
        
        for alt in alternates:
            match = re.match(r"^([A-G][#b]?m?(?:add\d+)?)(?:\((\d+)\))?$", alt)
            if match:
                base = match.group(1)
                forced = match.group(2)
                print(f"  Parsed: base='{base}', forced='{forced}'")
                if forced is not None:
                    # Store as a list to allow multiple variations per chord
                    if base not in requested_variations:
                        requested_variations[base] = []
                    requested_variations[base].append(int(forced))
                    print(f"  Added to requested_variations: {base} -> {requested_variations[base]}")
            else:
                print(f"  FAILED to parse alternate: '{alt}'")

    # Build request map from inline chords (can override suggested_alternate)
    for ch in raw_used:
        cleaned = normalize_chord(clean_chord(ch))
        base, forced = parse_requested_variation(cleaned)
        if forced is not None:
            if base not in requested_variations:
                requested_variations[base] = []
            if forced not in requested_variations[base]:
                requested_variations[base].append(forced)

    # 🐛 DEBUG
    print(f"Final requested_variations map: {requested_variations}")

    # ------------------------------------------------------------
    # Normalize + transpose the chords
    # ------------------------------------------------------------
    used_cleaned = [normalize_chord(clean_chord(ch)).strip() for ch in raw_used]
    transposed_chords = {
        transpose_chord(clean_chord(ch).strip(), transpose_value).strip()
        for ch in used_cleaned
    }

    # 🐛 DEBUG
    print(f"Transposed chords: {transposed_chords}")

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

    print(f"Final relevant_chords count: {len(relevant_chords)}")
    print("=" * 60)
    return relevant_chords
