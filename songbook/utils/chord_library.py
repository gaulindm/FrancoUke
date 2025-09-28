import json
import re
from pathlib import Path

# Base directory where chord JSON files live
CHORDS_DIR = Path(__file__).resolve().parent.parent / "chords"


def load_chords(instrument: str = "ukulele") -> list[dict]:
    """
    Load chord definitions for a specific instrument.
    
    Returns a list of chord dictionaries as stored in the JSON file.
    """
    filepath = CHORDS_DIR / f"{instrument}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"No chord library found for instrument '{instrument}'")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_chord_dict(instrument: str = "ukulele") -> dict[str, dict]:
    """
    Load chord definitions as a dictionary for quick lookups.
    Keys are chord names, values are chord objects.
    """
    return {ch["name"]: ch for ch in load_chords(instrument)}


def load_all_chords() -> dict[str, list[dict]]:
    """
    Load all available instruments' chord libraries.

    Returns:
        dict where keys = instrument names (e.g., 'ukulele'),
        values = list of chord dicts.
    """
    all_chords = {}
    for json_file in CHORDS_DIR.glob("*.json"):
        instrument = json_file.stem  # e.g., "ukulele", "banjo"
        with open(json_file, "r", encoding="utf-8") as f:
            all_chords[instrument] = json.load(f)
    return all_chords


def extract_relevant_chords(lyrics_with_chords, instrument: str = "ukulele") -> list[dict]:
    """
    Extract unique chords from a song's lyrics_with_chords and
    return only the chords found in the instrument's chord library.
    
    Args:
        lyrics_with_chords (list): Parsed lyrics with chord/lyric blocks.
        instrument (str): Instrument name, defaults to "ukulele".
    
    Returns:
        list[dict]: List of chord objects with name + variations.
    """
    chord_library = load_chord_dict(instrument)

    # Flatten lyrics into raw text with [CHORD] markup
    raw_lines = []
    for block in lyrics_with_chords:
        if isinstance(block, list):
            for item in block:
                if "chord" in item:
                    raw_lines.append(f"[{item['chord']}]")
                if "lyric" in item:
                    raw_lines.append(item["lyric"])
            raw_lines.append("\n")
    raw_lyrics = "".join(raw_lines)

    # Extract chords inside [ ... ]
    chord_pattern = re.compile(r"\[([A-G][#b]?(?:m|min|maj7|sus4|dim|aug|\d)*)\]")
    found_chords = chord_pattern.findall(raw_lyrics)
    unique_chords = sorted(set(found_chords))

    # Match against library
    return [
        {"name": name, "variations": chord_library[name]["variations"]}
        for name in unique_chords if name in chord_library
    ]
