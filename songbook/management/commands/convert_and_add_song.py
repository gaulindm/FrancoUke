import re
from pathlib import Path
from django.core.management.base import BaseCommand
from songbook.models import Song
from django.contrib.auth.models import User
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Convert ChordPro format, add metadata, and save the song to the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="Path to the input file containing the song"
        )
        parser.add_argument(
            "contributor_id", type=int, help="ID of the user contributing the song"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        contributor_id = kwargs["contributor_id"]

        try:
            # Resolve relative paths to the commands directory
            command_dir = Path(__file__).parent
            absolute_path = Path(file_path)
            if not absolute_path.is_absolute():
                file_path = command_dir / file_path

            # Read the input file
            with open(file_path, "r") as file:
                lines = file.readlines()

            if len(lines) < 2:
                raise ValueError("Input file must have at least two lines for artist and title.")

            # Extract artist and title
            artist = lines[0].strip()
            title = lines[1].strip()
            content = "".join(lines[2:])

            # Convert ChordPro format
            converted_content = re.sub(r"\{\{(.*?)\}\}", r"[\1]", content)

            # Prepare metadata as a string
            metadata_str = f"""{{title: {title}}}
{{artist: {artist}}}
{{album: }}
{{youtube:}}
{{capo: }}
{{composer: }}
{{lyricist: }}
{{key: }}
{{recording: }}
{{year: }}
{{1stnote: }}
{{tempo: }}
{{timeSignature: }}"""

            # Combine metadata and converted content
            song_chordpro = metadata_str + "\n\n" + converted_content

            # Prepare metadata as JSON
            metadata = {"artist": artist, "title": title}

            # Retrieve contributor (user)
            contributor = User.objects.get(pk=contributor_id)

            # Create the song in the database
            Song.objects.create(
                songTitle=title,
                songChordPro=song_chordpro,
                metadata=metadata,
                date_posted=now(),
                contributor=contributor,
            )

            self.stdout.write(self.style.SUCCESS(f"Song '{title}' by {artist} added successfully."))

        except User.DoesNotExist:
            self.stderr.write(f"Error: Contributor with ID {contributor_id} does not exist.")
        except FileNotFoundError:
            self.stderr.write(f"Error: File '{file_path}' not found.")
        except ValueError as e:
            self.stderr.write(f"Error: {e}")
        except Exception as e:
            self.stderr.write(f"An unexpected error occurred: {e}")
