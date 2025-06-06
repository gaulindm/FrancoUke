import os
import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from songbook.models import Song

class Command(BaseCommand):
    help = "Import ChordPro files into the Song model"

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Path to the directory containing ChordPro files')

    def handle(self, *args, **kwargs):
        directory = kwargs['directory']

        # Ensure the directory exists
        if not os.path.isdir(directory):
            self.stderr.write(f"Directory '{directory}' does not exist.")
            return

        files_imported = 0
        for filename in os.listdir(directory):
            if filename.endswith('.chordpro'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Parse metadata including artist
                dummy_song = Song(songChordPro=content)
                song_title, metadata = dummy_song.parse_metadata_from_chordpro()
                artist_name = metadata.get('artist', "Unknown Artist").strip()
                print(f"Extracted artist: {artist_name}")  # Debug statement

                # Fetch or create the contributor based on the artist name
                if artist_name != "Unknown Artist":
                    contributor, created = User.objects.get_or_create(username=artist_name)
                else:
                    self.stderr.write(f"No artist found in {filename}. Skipping file.")
                    continue

                print(f"Contributor: {contributor.username}, Created: {created}")  # Debug statement

                # Handle duplicates and create/update the song record
                song = Song.objects.filter(songTitle=song_title.strip()).first()
                if song:
                    song.songChordPro = content.strip()
                    song.contributor = contributor
                    song.save()
                    print(f"Updated song: {song.songTitle}")  # Debug statement
                else:
                    Song.objects.create(
                        songTitle=song_title.strip(),
                        songChordPro=content.strip(),
                        contributor=contributor,
                        metadata=metadata
                    )
                    print(f"Created new song: {song_title}")  # Debug statement

                files_imported += 1

        self.stdout.write(f"Successfully imported {files_imported} ChordPro files.")
