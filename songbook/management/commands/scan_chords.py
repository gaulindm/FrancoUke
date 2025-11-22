from django.core.management.base import BaseCommand
from songbook.models import Song
import re

class Command(BaseCommand):
    help = "Scan all Song records and extract all unique chords used in songChordPro"

    # Match ANYTHING inside brackets [ ... ] that looks like a chord
    CHORD_REGEX = re.compile(
        r'\[([A-G][#b]?[a-zA-Z0-9+\-]*)\]'
    )

    def handle(self, *args, **options):
        all_chords = set()

        for song in Song.objects.all():
            text = song.songChordPro or ""
            # Extract chords in brackets
            matches = self.CHORD_REGEX.findall(text)
            for chord in matches:
                all_chords.add(chord.strip())

        # Output
        self.stdout.write("\n🎸 ALL UNIQUE CHORDS USED IN DATABASE:")
        for chord in sorted(all_chords):
            self.stdout.write(f"  {chord}")

        self.stdout.write(f"\nTotal unique chords: {len(all_chords)}\n")
