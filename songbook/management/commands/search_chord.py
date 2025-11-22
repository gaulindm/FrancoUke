from django.core.management.base import BaseCommand
from songbook.models import Song
import re

class Command(BaseCommand):
    help = "Search for any bracketed chord-like token across all songs."

    def add_arguments(self, parser):
        parser.add_argument("token", type=str, help="Chord or token to search for, e.g. 'Feb-ru-ar-y' or 'Fadd9'")

    def handle(self, *args, **options):
        token = options["token"]
        pattern = re.compile(rf'\[{re.escape(token)}\]')

        self.stdout.write(f"\n🔍 Searching for: [{token}]\n")

        found = False

        for song in Song.objects.all():
            text = song.songChordPro or ""

            if re.search(pattern, text):
                found = True
                self.stdout.write(f"🎵 Found in: {song.songTitle} (ID {song.id})")

                # Show lines where it occurs
                for line in text.splitlines():
                    if re.search(pattern, line):
                        self.stdout.write(f"   ➜ {line.strip()}")

                self.stdout.write("")  # spacer

        if not found:
            self.stdout.write("❌ No matches found.\n")
        else:
            self.stdout.write("✔️ Search complete.\n")
