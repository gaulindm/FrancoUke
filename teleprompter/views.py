import json
import logging
import re
from pathlib import Path
from django.shortcuts import render, get_object_or_404
from songbook.models import Song
from songbook.utils.teleprompter_renderer import render_lyrics_with_chords_html
from songbook.utils.chord_library import load_chord_dict
from songbook.utils.teleprompter_helpers import (
    clean_chord_name,
    with_maj_aliases,
    apply_html_color_markup,
)
from songbook.context_processors import site_context

logger = logging.getLogger(__name__)

# -----------------------------
# 🎵 Main Teleprompter View (WITH COLOR MARKUP SUPPORT)
# -----------------------------
def teleprompter_view(request, song_id, beginner=False):
    # `beginner` is no longer used: there is now a single teleprompter page
    # that switches between chords above / inline in the browser. The
    # argument is kept only so an old URL route that still passes
    # beginner=True doesn't raise an error.
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
            variations = full_library[name]["variations"]
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
        chord_position="above",  # the page switches Above/Inline with CSS
    )

    # -----------------------------
    # 🐛 DEBUG (only runs when the logger is set to DEBUG)
    # -----------------------------
    if logger.isEnabledFor(logging.DEBUG):
        color_tags = ['<r>', '<g>', '<y>', '<red>', '<blue>', '<green>',
                      '<pink>', '<orange>', '<purple>', '<h>']
        found_tags = [t for t in color_tags if t in lyrics_html]
        logger.debug("Song: %s | color tags in renderer output: %s",
                     song.songTitle, found_tags or "none")
        logger.debug("Before color markup (first 400 chars): %s", lyrics_html[:400])

    # -----------------------------
    # 🎨 Apply color markup transformations
    # -----------------------------
    lyrics_html = apply_html_color_markup(lyrics_html)
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("After color markup (first 400 chars): %s", lyrics_html[:400])
        logger.debug("Contains <span style=> tags: %s", "<span style=" in lyrics_html)

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
        "full_chord_library_json": json.dumps(full_library),
        "user_preferences_json": json.dumps(user_preferences),
        "initial_scroll_speed": song.scroll_speed or 40,
        **context_data,
    }

    template_name = "songbook/song_teleprompter.html"
    return render(request, template_name, context)