"""
Single source of truth for the song header (title block) shown in the PDF
and in the teleprompter.  Both call build_song_header(song), so the two can
never drift apart again.

Layout (3 columns):
    Row 0:  time signature | TITLE          | strumming pattern
    Row 1:  1st vocal note | songwriter      | short_instruction_1 (or "(/ = one strum)")
    Row 2:  count in       | recorded-by     | short_instruction_2
Row 1 / Row 2 are only shown when at least one of their cells has content.
"""
from songbook.utils.chords.loader import extract_used_chords


def _clean(value):
    """None / whitespace-only -> '' ; everything else -> stripped str."""
    return str(value if value is not None else "").strip()


def build_song_header(song, show_strumming=True):
    metadata = song.metadata or {}

    artist = _clean(metadata.get("artist"))
    songwriter = _clean(metadata.get("songwriter"))
    year = metadata.get("year")
    capo_value = metadata.get("capo")

    # --- "Recorded by" line (omitted entirely when there is no artist) ---
    recorded_by = ""
    if artist:
        if isinstance(capo_value, str) and capo_value.lower() == "based":
            recorded_by = f"Based on clip by {artist}"
        else:
            try:
                capo_value = int(capo_value)
            except (TypeError, ValueError):
                capo_value = 0
            if capo_value > 0:
                recorded_by = f"Capo ({capo_value}) to match the recording by {artist}"
            else:
                recorded_by = f"Matches the recording by {artist}"
        if year:
            recorded_by += f" ({year})"

    # --- Strumming pattern ---
    strumming = _clean(getattr(song, "default_strumming_pattern", ""))
    if not show_strumming:
        strumming = ""

    # --- Row 1, right: instruction 1 wins; slash-chord note is the fallback ---
    has_slash_chord = any(
        "/" in chord for chord in extract_used_chords(song.lyrics_with_chords)
    )
    instruction_1 = _clean(metadata.get("short_instruction_1"))
    row1_right = instruction_1 or ("(/ = one strum)" if has_slash_chord else "")

    first_note = _clean(metadata.get("1stnote"))
    count_in = _clean(metadata.get("count_in"))

    header = {
        "title": song.songTitle or "Untitled Song",
        "time_signature": _clean(metadata.get("timeSignature")),
        "strumming": strumming,
        "songwriter": songwriter,
        "first_note_text": f"1st vocal note: {first_note}" if first_note else "",
        "row1_right": row1_right,
        "count_in_text": f"Count in: {count_in}" if count_in else "",
        "recorded_by": recorded_by,
        "instruction_2": _clean(metadata.get("short_instruction_2")),
    }
    header["show_row1"] = bool(
        header["songwriter"] or header["first_note_text"] or header["row1_right"]
    )
    header["show_row2"] = bool(
        header["recorded_by"] or header["count_in_text"] or header["instruction_2"]
    )
    return header
