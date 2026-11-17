# songbook/management/commands/export_tagged_songs.py
"""
Export songs carrying any of the given tags as CSV, for planning in Sheets.

Examples:
    python manage.py export_tagged_songs
    python manage.py export_tagged_songs --output holiday_songs.csv
    python manage.py export_tagged_songs --tags holiday christmas xmas
    python manage.py export_tagged_songs --tags christ --contains
    python manage.py export_tagged_songs --include-hidden

Remember to quote tag names containing '&' in bash, e.g. --tags "Gospel&Spiritual".
"""
import csv
import io

from django.core.management.base import BaseCommand
from django.db.models import Q

from songbook.models import Song


class Command(BaseCommand):
    help = "Export songs with any of the given tags to CSV (stdout, or a file with --output)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tags",
            nargs="+",
            default=["holiday", "christmas"],
            help="Tag names to match (default: holiday christmas). Case-insensitive.",
        )
        parser.add_argument(
            "--contains",
            action="store_true",
            help="Match tags that contain the text instead of matching exactly "
                 "(e.g. --tags christ finds 'Christmas Songs').",
        )
        parser.add_argument(
            "--output",
            help="Write to this CSV file instead of printing to the screen.",
        )
        parser.add_argument(
            "--include-hidden",
            action="store_true",
            help="Also include songs hidden from all platforms (no site_name) "
                 "and private personal copies (is_public=False).",
        )

    def handle(self, *args, **options):
        lookup = "tags__name__icontains" if options["contains"] else "tags__name__iexact"
        tag_filter = Q()
        for tag in options["tags"]:
            tag_filter |= Q(**{lookup: tag})

        songs = Song.objects.filter(tag_filter)
        if not options["include_hidden"]:
            songs = songs.exclude(site_name__isnull=True).filter(is_public=True)

        # Extract distinct PKs first, then re-query. Filtering across the tags
        # M2M can return one row per matching tag (the JOIN duplication gotcha).
        pks = songs.values_list("pk", flat=True).distinct()
        songs = Song.objects.filter(pk__in=list(pks)).prefetch_related("tags").order_by("songTitle")

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Title", "Artist", "Key", "Chords", "Strumming", "Origin", "Tags"])

        count = 0
        for song in songs:
            meta = song.metadata or {}
            writer.writerow([
                song.songTitle or "",
                meta.get("artist", "") or "",
                song.effective_key or "",
                song.chords_used or "",
                song.default_strumming_pattern or "",
                song.origin or "",
                ", ".join(sorted(t.name for t in song.tags.all())),
            ])
            count += 1

        if options["output"]:
            # utf-8-sig adds a BOM so Excel/Sheets read accents and symbols correctly
            with open(options["output"], "w", encoding="utf-8-sig", newline="") as f:
                f.write(buffer.getvalue())
            self.stdout.write(self.style.SUCCESS(
                f"Wrote {count} songs to {options['output']}"
            ))
        else:
            self.stdout.write(buffer.getvalue())
            self.stderr.write(f"{count} songs")