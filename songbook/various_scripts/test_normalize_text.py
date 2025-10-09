# songbook/various_scripts/test_normalize_text.py

from songbook.utils.transposer import normalize_chords_in_text

test_song = """
[C]This is a [Em///] fake [A7////] song
With [D/F#] chords and [N.C.] breaks
And [CM7] and [Cmaj7////] both appear
"""

cleaned = normalize_chords_in_text(test_song)

print("🧹 Cleaned Song:")
print(cleaned)
