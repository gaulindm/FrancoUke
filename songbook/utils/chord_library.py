import json
from pathlib import Path

CHORDS_DIR = Path(__file__).resolve().parent.parent / "chords"

def load_chords(instrument="ukulele"):
    """Load chord definitions for a specific instrument."""
    filepath = CHORDS_DIR / f"{instrument}.json"
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_chords():
    """Load all instrument chord dictionaries."""
    all_chords = {}
    for json_file in CHORDS_DIR.glob("*.json"):
        instrument = json_file.stem  # "ukulele", "banjo", etc.
        with open(json_file, "r", encoding="utf-8") as f:
            all_chords[instrument] = json.load(f)
    return all_chords
