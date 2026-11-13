# setlist/management/commands/make_setlist_from_ack.py
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from songbook.models import Song
from setlists.models import SetList, SetListSong


class Command(BaseCommand):
    help = "Create a setlist from songs matching an origin and acknowledgement."

    def add_arguments(self, parser):
        parser.add_argument("--origin", default="FWC")
        parser.add_argument("--ack", default="Dave and Sarah of Ukulele Daily Strum")
        parser.add_argument("--name", default="Ukulele Daily Strum songs")
        parser.add_argument("--group-id", type=int, help="core.Group pk (optional)")
        parser.add_argument("--user", help="Username to record as created_by (optional)")
        parser.add_argument("--site", choices=["FrancoUke", "StrumSphere"],
                            help="Only include songs visible on this site (optional)")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **opts):
        songs = Song.objects.filter(
            origin__iexact=opts["origin"],
            acknowledgement__icontains=opts["ack"],
            is_public=True,
        )
        if opts["site"]:
            songs = songs.filter(site_name=opts["site"])
        songs = list(songs.order_by("songTitle"))

        self.stdout.write(f"{len(songs)} matching songs:")
        for s in songs:
            self.stdout.write(f"  {s.songTitle}  [{s.site_name or 'no site'}]")

        if not opts["apply"]:
            self.stdout.write("Dry run. Use --apply to create the setlist.")
            return

        if not songs:
            raise CommandError("No matching songs, nothing to create.")

        created_by = None
        if opts["user"]:
            User = get_user_model()
            try:
                created_by = User.objects.get(username=opts["user"])
            except User.DoesNotExist:
                raise CommandError(f"No user '{opts['user']}'.")

        if SetList.objects.filter(name=opts["name"], group_id=opts["group_id"]).exists():
            raise CommandError(f"A setlist named '{opts['name']}' already exists.")

        with transaction.atomic():
            setlist = SetList.objects.create(
                name=opts["name"],
                group_id=opts["group_id"],
                created_by=created_by,
            )
            SetListSong.objects.bulk_create(
                [SetListSong(setlist=setlist, song=s, order=i)
                 for i, s in enumerate(songs, start=1)]
            )

        self.stdout.write(self.style.SUCCESS(
            f"Created '{setlist.name}' with {len(songs)} songs."
        ))