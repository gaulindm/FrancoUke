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
    text = re.sub(r'</span></span>', '</span>', text)
    
    return text


# -----------------------------
# 🎵 Main Teleprompter View (WITH COLOR MARKUP SUPPORT)
# -----------------------------
def teleprompter_view(request, song_id, beginner=False):
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
        r"\[([A-G][#b]?(?:m|min|maj7|maj9|maj|sus2|sus4|dim|aug|\d)*(?:/[A-G#b]*)*/*)\]"
    )
    found_chords = chord_pattern.findall(raw_lyrics)

    # Normalize BEFORE deduplication
    normalized_map = {raw: clean_chord_name(raw) for raw in found_chords}
    normalized_unique = sorted(set(normalized_map.values()))

    # -----------------------------
    # 📚 Match chords to chord dictionary
    # -----------------------------
    relevant_chords = []
    for name in normalized_unique:
        if name in chord_library:
            variations = chord_library[name]["variations"]
            show_alt = bool(user_pref and getattr(user_pref, "is_printing_alternate_chord", False))

            if show_alt and len(variations) > 1:
                selected = [variations[1]]
            else:
                selected = [variations[0]]

            relevant_chords.append({
                "name": name,
                "variations": selected,
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
        chord_position="above" if beginner else "inline"
    )

    # -----------------------------
    # 🐛 DEBUG: Check for color tags
    # -----------------------------
    print("\n" + "=" * 80)
    print(f"🎵 SONG: {song.songTitle}")
    print("=" * 80)
    print("📝 BEFORE apply_html_color_markup (first 400 chars):")
    print(lyrics_html[:400])
    
    # Check if color tags exist in the raw output
    color_tags = ['<r>', '<g>', '<y>', '<red>', '<blue>', '<green>', '<pink>', '<orange>', '<purple>', '<h>']
    has_color_tags = any(tag in lyrics_html for tag in color_tags)
    print(f"\n🎨 Contains color tags? {has_color_tags}")
    
    if has_color_tags:
        print("✅ Color tags found in lyrics_html")
        for tag in color_tags:
            if tag in lyrics_html:
                print(f"   - Found: {tag}")
    else:
        print("❌ NO color tags found - checking raw JSON...")
        # Check the raw JSON
        if song.lyrics_with_chords:
            print("\n📋 Sample from lyrics_with_chords JSON:")
            for i, block in enumerate(song.lyrics_with_chords[:3]):  # First 3 blocks
                print(f"Block {i}: {block}")

    # -----------------------------
    # 🎨 Apply color markup transformations
    # -----------------------------
    lyrics_html = apply_html_color_markup(lyrics_html)
    
    # -----------------------------
    # 🐛 DEBUG: Verify transformation
    # -----------------------------
    print("\n" + "=" * 80)
    print("📝 AFTER apply_html_color_markup (first 400 chars):")
    print(lyrics_html[:400])
    
    # Check if span tags were created
    has_span_tags = '<span style=' in lyrics_html
    print(f"\n🎨 Contains <span style=> tags? {has_span_tags}")
    
    if has_span_tags:
        print("✅ Color markup successfully converted to HTML spans")
    else:
        print("⚠️ No span tags found - color markup may not have been applied")
    
    print("=" * 80 + "\n")

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
        # Full dictionary for this instrument (not just this song's chords).
        # Needed so the teleprompter can look up a *real* diagram for a
        # chord after transposing, instead of just sliding the original
        # shape up/down the neck.
        "full_chord_library_json": json.dumps(chord_library),
        "user_preferences_json": json.dumps(user_preferences),
        "initial_scroll_speed": song.scroll_speed or 40,
        **context_data,
    }

    template_name = (
        "songbook/teleprompter_beginner.html" if beginner
        else "songbook/teleprompter.html"
    )
    return render(request, template_name, context)