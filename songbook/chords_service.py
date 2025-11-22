import os
import json
from django.conf import settings

CHORD_DIR = os.path.join(settings.BASE_DIR, "songbook", "chords")


def _file_path(instrument):
    return os.path.join(CHORD_DIR, f"{instrument}.json")


def load_chords(instrument):
    path = _file_path(instrument)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_chords(instrument, data):
    path = _file_path(instrument)
    temp = path + ".tmp"
    with open(temp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(temp, path)
