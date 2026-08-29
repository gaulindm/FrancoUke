# songbook/management/commands/backfill_detected_keys.py

from django.core.management.base import BaseCommand

from songbook.models import Song
from songbook.parsers import parse_song_data
from songbook.utils.transposer import detect_key, extract_chords


class Command(BaseCommand):
    help = (
        "Backfill Song.detected_key for existing songs. detected_key is normally "
        "computed automatically in Song.save(), so songs created before that field "
        "existed will have it blank until re-saved. This command previews (and, with "
        "--apply, performs) that backfill without needing to touch every song by hand. "
        "Dry-run by default."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually save the changes. Without this flag, only a preview is printed.",
        )
        parser.add_argument(
            "--site",
            type=str,
            default=None,
            help="Optional site_name filter, e.g. StrumSphere or FrancoUke. Defaults to all sites.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        site_filter = options["site"]

        songs = Song.objects.all().order_by("songTitle")
        if site_filter:
            songs = songs.filter(site_name=site_filter)

        total = songs.count()
        changed = 0
        no_chords = 0

        site_label = f" for site '{site_filter}'" if site_filter else ""
        self.stdout.write(f"Scanning {total} song(s){site_label}...\n")

        for song in songs:
            if not song.songChordPro:
                continue

            # Mirror the same logic Song.save() uses, so the preview matches
            # exactly what would be written.
            lyrics_with_chords = parse_song_data(song.songChordPro)
            all_chords = extract_chords(lyrics_with_chords, unique=False)
            new_key = detect_key(lyrics_with_chords) if all_chords else None

            old_key = song.detected_key

            if not all_chords:
                no_chords += 1

            if new_key != old_key:
                changed += 1
                self.stdout.write(
                    f"  {song.songTitle!r} (pk={song.pk}, site={song.site_name}): "
                    f"{old_key or '(none)'} -> {new_key or '(none)'}"
                )
                if apply_changes:
                    # Full save() so detected_key is set the same way it would
                    # be on any normal edit - keeps this command from drifting
                    # out of sync with Song.save() over time.
                    song.save()

        self.stdout.write("")
        if apply_changes:
            self.stdout.write(self.style.SUCCESS(
                f"Done. Updated detected_key for {changed} of {total} song(s)."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"Dry run: {changed} of {total} song(s) would be updated. "
                f"Re-run with --apply to save changes."
            ))

        if no_chords:
            self.stdout.write(
                f"Note: {no_chords} song(s) have no chords and will have detected_key = None."
            )