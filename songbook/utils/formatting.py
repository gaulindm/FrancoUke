import json
import re
from pathlib import Path
from django.shortcuts import render, get_object_or_404
from songbook.models import Song
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html
from songbook.utils.chord_library import load_chord_dict
from songbook.context_processors import site_context

# -----------------------------
# 🎨 Color Markup Helper
# -----------------------------
def apply_html_color_markup(text):
    """
    Convert custom color tags to HTML for web display.
    Similar to PDF apply_color_markup but outputs span tags.
    """
    if not text:
        return text
    
    color_map = {
        'red': 'red',
        'blue': 'blue',
        'green': 'green',
        'yellow': 'gold',
        'orange': 'orange',
        'pink': 'hotpink',
        'purple': 'purple',
    }
    
    # Full color names: <red>text</red> → <span style='color:red'>text</span>
    for tag, color in color_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<span style='color:{color}'>{m.group(1)}</span>", text)
    
    # Short color codes: <r>text</r> → <span style='color:red'>text</span>
    short_map = {'r': 'red', 'g': 'green', 'y': 'gold'}
    for tag, color in short_map.items():
        pattern = re.compile(rf'<{tag}>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
        text = pattern.sub(lambda m: f"<span style='color:{color}'>{m.group(1)}</span>", text)
    
    # Custom highlight: <highlight color="blue">text</highlight>
    pattern = re.compile(r'<highlight\s+color="(.*?)">(.*?)</highlight>', re.IGNORECASE | re.DOTALL)
    text = pattern.sub(lambda m: f"<span style='background-color:{m.group(1)}'>{m.group(2)}</span>", text)
    
    # Simple highlight: <h>text</h> → yellow background
    text = re.sub(r'<h>(.*?)</h>', r"<span style='background-color:yellow'>\1</span>", text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up any nested closing tags
    text = re.sub(r'</span>\s*</span>', '</span>', text)
    
    return text


# -----------------------------
# 🧠 Helper: normalize chord names
# -----------------------------
def clean_chord_name(chord: str) -> str:
    """Normalize chord notation for consistent matching with chord library.

    Major-seventh style chords are standardized on the "maj" spelling:
    CM7, CMaj7, CΔ7 and Cmaj7 all become Cmaj7.
    """
    if not chord:
        return chord

    chord = chord.strip()

    # Remove trailing slashes (Em///)
    chord = re.sub(r"/+$", "", chord)
    # Remove bass notes like D/F#
    chord = re.sub(r"/[A-G][#b]?$", "", chord)

    # --- Normalize chord quality naming ---
    # Maj7, MAJ7 → maj7
    chord = re.sub(r"(?i)maj", "maj", chord)
    # Capital M after the root, followed by a number: CM7 → Cmaj7, F#M9 → F#maj9
    chord = re.sub(r"(?<=[A-G#b])M(?=\d)", "maj", chord)
    # Jazz delta symbols → maj
    chord = chord.replace("Δ", "maj").replace("△", "maj")
    # min → m
    chord = re.sub(r"(?i)min", "m", chord)

    # Standardize capitalization (e.g., fm7 → Fm7)
    chord = chord.strip().replace(" ", "")
    if len(chord) > 1:
        chord = chord[0].upper() + chord[1:]
    else:
        chord = chord.upper()

    return chord


# -----------------------------
# 📚 Helper: find a chord under either major-seventh spelling
# -----------------------------
_MAJ_STYLE = re.compile(r"(?i:maj)|(?<=[A-G#b])M(?=\d)|[Δ△]")


def with_maj_aliases(chord_library):
    """Return a copy of the chord library in which every major-seventh style
    chord can be found under BOTH spellings (Cmaj7 and CM7).

    That way the songs and the library don't have to agree on the spelling
    while you convert your data, and transposing (which looks chords up by
    exact name) keeps working either way.
    """
    result = dict(chord_library)
    for key, value in chord_library.items():
        if not _MAJ_STYLE.search(key):
            continue
        canonical = clean_chord_name(key)                    # CM7   → Cmaj7
        legacy = re.sub(r"maj(?=\d)", "M", canonical)        # Cmaj7 → CM7
        result.setdefault(canonical, value)
        result.setdefault(legacy, value)
    return result


# -----------------------------
# 🎵 Main Teleprompter View (CLEAN FIXED VERSION)
# -----------------------------
def teleprompter_view(request, song_id):
    song = get_object_or_404(Song, pk=song_id)

    # -----------------------------
    # 👤 User preference (get first!)
    # -----------------------------
    user_pref = getattr(request.user, "userpreference", None)

    # -----------------------------
    # 🎸 Determine instrument
    # -----------------------------
    instrument = request.GET.get("instrument")

    if not instrument and user_pref:
        instrument = getattr(user_pref, "primary_instrument", "ukulele")

    instrument = instrument or "ukulele"
    chord_library = load_chord_dict(instrument)

    # -----------------------------
    # 📝 Convert lyrics_with_chords JSON to raw lyric-text with [chords]
    # -----------------------------
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
    # 🎸 Extract chords
    # -----------------------------
    chord_pattern = re.compile(
        r"\[([A-G][#b]?(?:maj|min|add|sus|dim|aug|[mM+]|\d|[#b])*(?:/[A-G#b]*)*/*)\]"
    )
    found_chords = chord_pattern.findall(raw_lyrics)

    # Normalize BEFORE deduplication
    normalized_map = {raw: clean_chord_name(raw) for raw in found_chords}
    normalized_unique = sorted(set(normalized_map.values()))

    # -----------------------------
    # 📚 Match chords to chord dictionary
    # -----------------------------
    # Indexed under both "maj7" and "M7" spellings (see with_maj_aliases).
    full_library = with_maj_aliases(chord_library)

    relevant_chords = []
    for name in normalized_unique:
        if name in full_library:
            relevant_chords.append({
                "name": name,
                "variations": full_library[name]["variations"],
            })

    # -----------------------------
    # 🎯 Known-chord filtering
    # -----------------------------
    if user_pref and getattr(user_pref, "use_known_chord_filter", False):
        known_chords = getattr(user_pref, "known_chords", []) or []
        known_clean = set(clean_chord_name(ch).lower() for ch in known_chords)

        relevant_chords = [
            chord for chord in relevant_chords
            if clean_chord_name(chord["name"]).lower() not in known_clean
        ]

    # -----------------------------
    # 🌐 Site context
    # -----------------------------
    context_data = site_context(request)
    site_name = context_data["site_name"]

    # -----------------------------
    # 🧾 Render lyrics HTML
    # -----------------------------
    lyrics_html, metadata = render_lyrics_with_chords_html(
        song.lyrics_with_chords,
        site_name,
        chord_position="above",  # the page switches Above/Inline with CSS
    )

    # -----------------------------
    # 🎨 Apply color markup transformations
    # -----------------------------
    lyrics_html = apply_html_color_markup(lyrics_html)

    # -----------------------------
    # 🛠 User prefs (sent to JS)
    # -----------------------------
    user_preferences = {
        "instrument": instrument,
        "isLefty": getattr(user_pref, "is_lefty", False),
        "showAlternate": getattr(user_pref, "is_printing_alternate_chord", False),
        "useKnownChordFilter": getattr(user_pref, "use_known_chord_filter", False),
        "knownChords": getattr(user_pref, "known_chords", []),
    }

    # -----------------------------
    # 🧩 Final context
    # -----------------------------
    context = {
        "song": song,
        "lyrics_with_chords": lyrics_html,
        "metadata": metadata,
        "relevant_chords_json": json.dumps(relevant_chords),
        "full_chord_library_json": json.dumps(full_library),
        "user_preferences_json": json.dumps(user_preferences),
        "initial_scroll_speed": song.scroll_speed or 40,
        **context_data,
    }

    return render(request, "songbook/teleprompter_unified.html", context)