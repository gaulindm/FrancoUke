from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from songbook.models import Song, SongFormatting


class Command(BaseCommand):
    help = (
        "Create default SongFormatting rows for a user on visible songs that "
        "they haven't formatted yet (same as opening the formatting page and "
        "saving without changes). Dry-run by default; use --apply to write."
    )

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True, help="Username the formatting is saved under")
        parser.add_argument("--apply", action="store_true", help="Actually write changes")
        parser.add_argument("--site", default="FrancoUke", help="site_name (default: FrancoUke)")
        parser.add_argument("--exclude-tag", action="append", default=[],
                            help="Skip songs with this tag (repeatable), e.g. --exclude-tag Hidden")
        parser.add_argument("--origin", help="Also restrict to this origin (e.g. SOUP)")
        parser.add_argument("--limit", type=int, help="Only process the first N songs")

    def handle(self, *args, **opts):
        User = get_user_model()
        try:
            user = User.objects.get(username=opts["user"])
        except User.DoesNotExist:
            raise CommandError(f"No user named {opts['user']!r}")

        qs = Song.objects.filter(
            site_name=opts["site"],
            is_public=True,
        ).exclude(songformatting__user=user)

        if opts["origin"]:
            qs = qs.filter(origin=opts["origin"])
        for tag in opts["exclude_tag"]:
            qs = qs.exclude(tags__name__iexact=tag)

        # Distinct PKs first, to avoid JOIN duplication
        pks = list(qs.values_list("pk", flat=True).distinct().order_by("pk"))
        if opts["limit"]:
            pks = pks[: opts["limit"]]

        self.stdout.write(f"{len(pks)} {opts['site']} songs without formatting for {user.username}.")

        if not opts["apply"]:
            for song in Song.objects.filter(pk__in=pks).order_by("songTitle")[:20]:
                self.stdout.write(f"  would format: {song.songTitle} ({song.origin})")
            if len(pks) > 20:
                self.stdout.write(f"  ... and {len(pks) - 20} more")
            self.stdout.write(self.style.WARNING("Dry run. Re-run with --apply to write."))
            return

        created = 0
        with transaction.atomic():
            for song in Song.objects.filter(pk__in=pks):
                _, was_created = SongFormatting.objects.get_or_create(user=user, song=song)
                created += was_created

        self.stdout.write(self.style.SUCCESS(f"Created {created} SongFormatting rows."))