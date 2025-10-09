# songbook/various_scripts/test_chord_cleanup.py
from songbook.utils.transposer import normalize_chords_in_text

def test_chord_cleanup():
    input_text = """
    [C]This is a [Em///] fake [A7////] song
    With [D/F#] chords and [N.C.] breaks
    And [CM7] and [Cmaj7] both appear
    """
    expected = """
    [C]This is a [Em] fake [A7] song
    With [D] chords and [N.C.] breaks
    And [CM7] and [Cmaj7] both appear
    """
    assert normalize_chords_in_text(input_text).strip() == expected.strip()
