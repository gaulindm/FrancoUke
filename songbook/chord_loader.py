# songbook/chord_loader.py
import json
from pathlib import Path
from django.conf import settings

# Change this to point where your chord JSON files live on disk.
# Default: <project_root>/songbook/chords/*.json
CHORD_DIR = Path(settings.BASE_DIR) / "songbook" / "chords"
CHORD_DIR.mkdir(parents=True, exist_ok=True)


def load_all_chords():
    """
    Load all chord JSON files into a dictionary:
      { "ukulele": [ {...}, ... ], "guitar": [...], ... }
    If file invalid, returns empty list for that instrument.
    """
    all_chords = {}
    for path in sorted(CHORD_DIR.glob("*.json")):
        instrument = path.stem
        try:
            with open(path, "r", encoding="utf-8") as fh:
                all_chords[instrument] = json.load(fh)
        except Exception as e:
            # Keep an empty list so the front-end knows the instrument exists
            print(f"[chord_loader] error loading {path}: {e}")
            all_chords[instrument] = []
    return all_chords


def save_all_chords(chords_dict):
    """
    Save dictionary back to individual JSON files.
    chords_dict should be: { instrument_name: [ {name, variations}, ... ] }
    """
    for instrument, data in chords_dict.items():
        out = CHORD_DIR / f"{instrument}.json"
        try:
            tmp = out.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            tmp.replace(out)
            print(f"[chord_loader] saved {out}")
        except Exception as e:
            print(f"[chord_loader] error saving {instrument} -> {out}: {e}")
            raise
