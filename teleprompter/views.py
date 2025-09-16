# views.py
import json
import re
from pathlib import Path
from django.shortcuts import render, get_object_or_404
from songbook.models import Song
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html

# Correct location of your JSON chord files
CHORDS_DIR = Path(__file__).resolve().parent.parent / "songbook" / "chords"


def load_chord_library(instrument="ukulele"):
    chords_file = CHORDS_DIR / f"{instrument}.json"
    with open(chords_file, "r", encoding="utf-8") as f:
        return {ch["name"]: ch for ch in json.load(f)}


def teleprompter_view(request, song_id):
    song = get_object_or_404(Song, pk=song_id)

    # Load correct chord library
    chord_library = load_chord_library("ukulele")  # 🔜 make this dynamic later

    # Convert Song.lyrics_with_chords (list of lists) into raw text
    raw_lines = []
    for block in song.lyrics_with_chords:
        if isinstance(block, list):
            for item in block:
                if "chord" in item:
                    raw_lines.append(f"[{item['chord']}]")
                if "lyric" in item:
                    raw_lines.append(item["lyric"])
            raw_lines.append("\n")
    raw_lyrics = "".join(raw_lines)

    # Extract chords from ChordPro-style brackets
    chord_pattern = re.compile(r"\[([A-G][#b]?(?:m|min|maj7|sus4|dim|aug|\d)*)\]")
    found_chords = chord_pattern.findall(raw_lyrics)
    unique_chords = sorted(set(found_chords))

    # Match against chord library
    relevant_chords = []
    for chord_name in unique_chords:
        if chord_name in chord_library:
            chord_obj = {
                "name": chord_name,
                "variations": chord_library[chord_name]["variations"],
            }
            relevant_chords.append(chord_obj)

    # Render pretty lyrics + metadata
    lyrics_html, metadata = render_lyrics_with_chords_html(
        song.lyrics_with_chords, "FrancoUke"
    )

    return render(
        request,
        "songbook/teleprompter.html",
        {
            "song": song,
            "lyrics_with_chords": lyrics_html,
            "metadata": metadata,
            "relevant_chords_json": json.dumps(relevant_chords),  # ⬅️ pass raw list, not json.dumps
        },
    )
