from django.core.management.base import BaseCommand
from django.db import transaction
from taggit.models import Tag

from songbook.models import Song


class Command(BaseCommand):
    help = "Replace the 'Xmas' tag with 'Holiday' on all songs (dry run unless --apply)."

    def add_arguments(self, parser):
        parser.add_argument("--old", default="Xmas", help="Tag to replace (default: Xmas)")
        parser.add_argument("--new", default="Holiday", help="Replacement tag (default: Holiday)")
        parser.add_argument("--apply", action="store_true", help="Actually make the changes")
        parser.add_argument(
            "--delete-old-tag",
            action="store_true",
            help="Also delete the now-unused old Tag object (only with --apply)",
        )

    def handle(self, *args, **opts):
        old, new, apply = opts["old"], opts["new"], opts["apply"]

        # Distinct PKs first, to avoid duplicate rows from the M2M join
        pks = list(
            Song.objects.filter(tags__name=old)
            .values_list("pk", flat=True)
            .distinct()
        )

        if not pks:
            self.stdout.write(self.style.WARNING(f"No songs tagged '{old}'."))
            return

        self.stdout.write(f"{len(pks)} song(s) tagged '{old}':")
        songs = Song.objects.filter(pk__in=pks)

        if not apply:
            for song in songs:
                self.stdout.write(f"  would retag: {song}")
            self.stdout.write(self.style.WARNING("Dry run only. Re-run with --apply to make changes."))
            return

        with transaction.atomic():
            for song in songs:
                song.tags.remove(old)
                song.tags.add(new)      # pass the string directly, not unpacked
                self.stdout.write(f"  retagged: {song}")

            if opts["delete_old_tag"]:
                deleted, _ = Tag.objects.filter(name=old).delete()
                self.stdout.write(f"Deleted old tag '{old}' ({deleted} object(s) removed).")

        self.stdout.write(self.style.SUCCESS(f"Done: {len(pks)} song(s) now tagged '{new}'."))