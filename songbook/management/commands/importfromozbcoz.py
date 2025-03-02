import os
from django.core.management.base import BaseCommand
from songbook.models import Song

class Command(BaseCommand):
    help = 'Import .pro files into the songChordPro field, adding metadata placeholders'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory containing .pro files')

    def handle(self, *args, **kwargs):
        directory = kwargs['directory']

        if not os.path.exists(directory):
            self.stderr.write(f"The directory '{directory}' does not exist.")
            return

        # Metadata template to insert after title and artist
        metadata_template = """\
{album: }
{youtube: }
{capo: }
{songwriter: }
{key: }
{capo: }
{year: }
{1stnote: }
{tempo: }
{timeSignature: }
"""

        for filename in os.listdir(directory):
            if filename.endswith('.pro'):
                file_path = os.path.join(directory, filename)
                self.stdout.write(f"Processing file: {file_path}")

                # Read the file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                        self.stdout.write(f"File content read successfully: {len(file_content)} characters")
                except Exception as e:
                    self.stderr.write(f"Error reading file {file_path}: {e}")
                    continue

                # Replace {t:} with {title:} in the content
                file_content = file_content.replace('{t:', '{title:')

                # Use the file name (without extension) as the title
                song_title = os.path.splitext(filename)[0]
                self.stdout.write(f"Title: {song_title}")

                # Default artist (modify as needed or parse from content)
                artist = "Unknown Artist"  # You may replace this with actual logic if artist info is available

                # Combine title, artist, metadata template, and file content
                song_chord_pro_content = f"{metadata_template}\n{file_content}"

                # Hardcoded contributor ID
                contributor_id = 1

                # Create or get the song
                try:
                    song, created = Song.objects.get_or_create(
                        songTitle=song_title,
                        defaults={
                            'songChordPro': song_chord_pro_content,
                            'contributor_id': contributor_id,
                        },
                    )

                    if created:
                        self.stdout.write(f"Created new song: {song_title}")
                    else:
                        self.stdout.write(f"Song already exists: {song_title}, updating songChordPro field")
                        song.songChordPro = song_chord_pro_content
                        song.save()

                    # Verify the field was saved
                    saved_song = Song.objects.get(songTitle=song_title)
                    if saved_song.songChordPro == song_chord_pro_content:
                        self.stdout.write(f"songChordPro successfully updated for '{song_title}'")
                    else:
                        self.stderr.write(f"songChordPro mismatch for '{song_title}'")
                        self.stderr.write(f"Expected: {len(song_chord_pro_content)} characters")
                        self.stderr.write(f"Found: {len(saved_song.songChordPro or '')} characters")

                except Exception as e:
                    self.stderr.write(f"Error saving song '{song_title}': {e}")
