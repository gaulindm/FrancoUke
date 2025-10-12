import json
import re
from pathlib import Path
from django.shortcuts import render, get_object_or_404
from songbook.models import Song
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html
from songbook.utils.chord_library import load_chord_dict
from songbook.context_processors import site_context

# -----------------------------
# 🧠 Helper: normalize chord names
# -----------------------------

def clean_chord_name(chord: str) -> str:
    """Normalize chord notation for consistent matching with chord library."""
    if not chord:
        return chord

    chord = chord.strip()

    # Remove trailing slashes (Em///)
    chord = re.sub(r"/+$", "", chord)
    # Remove bass notes like D/F#
    chord = re.sub(r"/[A-G][#b]?$", "", chord)

    # --- Normalize chord quality naming ---
    # maj7, Maj7, MAJ7 → M7  (and same for maj9, etc.)
    chord = re.sub(r"(?i)maj(?=\d*)", "M", chord)
    # min → m
    chord = re.sub(r"(?i)min", "m", chord)
    # Jazz delta symbol → M
    chord = chord.replace("Δ", "M")

    # Standardize capitalization (e.g., fm7 → Fm7)
    chord = chord.strip().replace(" ", "")
    if len(chord) > 1:
        chord = chord[0].upper() + chord[1:]
    else:
        chord = chord.upper()

    return chord



# -----------------------------
# 🎵 Main Teleprompter View
# -----------------------------
def teleprompter_view(request, song_id):
    song = get_object_or_404(Song, pk=song_id)

    # Determine instrument
    instrument = request.GET.get("instrument")
    if not instrument and request.user.is_authenticated:
        instrument = getattr(request.user.userpreference, "primary_instrument", "ukulele")
    instrument = instrument or "ukulele"

    chord_library = load_chord_dict(instrument)

    # Convert lyrics_with_chords JSON into raw text
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

    # -----------------------------
    # 🎸 Extract chords from raw lyrics
    # -----------------------------
    chord_pattern = re.compile(
        r"\[([A-G][#b]?(?:m|min|maj7|maj9|maj|sus2|sus4|dim|aug|\d)*(?:/[A-G#b]*)*/*)\]"
    )
    found_chords = chord_pattern.findall(raw_lyrics)

    # 🧹 Normalize chords *before* deduplication
    normalized_map = {raw: clean_chord_name(raw) for raw in found_chords}
    normalized_unique = sorted(set(normalized_map.values()))

    print("\n🎶 Found chords:")
    for raw, norm in normalized_map.items():
        print(f"   {raw:<10} → {norm}")
    print(f"✅ Total unique (normalized): {len(normalized_unique)}\n")

    # 🎸 Match to chord library
    relevant_chords = []
    for name in normalized_unique:
        if name in chord_library:
            relevant_chords.append({
                "name": name,
                "variations": chord_library[name]["variations"],
            })
        else:
            print(f"⚠️ Missing chord in library: {name}")


    # Site context
    context_data = site_context(request)
    site_name = context_data["site_name"]

    # Render lyrics with chords HTML
    lyrics_html, metadata = render_lyrics_with_chords_html(song.lyrics_with_chords, site_name)

    # User preferences
    user_pref = getattr(request.user, "userpreference", None)
    user_preferences = {
        "instrument": getattr(user_pref, "primary_instrument", "ukulele"),
        "isLefty": getattr(user_pref, "is_lefty", False),
        "showAlternate": getattr(user_pref, "is_printing_alternate_chord", False),
    }

    # -----------------------------
    # 🧩 Final context for JS + template
    # -----------------------------
    context = {
        "song": song,
        "lyrics_with_chords": lyrics_html,
        "metadata": metadata,
        "relevant_chords_json": json.dumps(relevant_chords),
        "user_preferences_json": json.dumps(user_preferences),
        "initial_scroll_speed": song.scroll_speed or 40,
        **context_data,
    }

    return render(request, "songbook/teleprompter.html", context)
