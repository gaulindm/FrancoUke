# songbook/management/commands/export_unformatted_titles.py      (run on PRODUCTION)
import json
from django.core.management.base import BaseCommand
from songbook.models import Song, SongFormatting
from songbook.sync_utils import sha1_text


class Command(BaseCommand):
    help = "PRODUCTION: list the songs that still need formatting (id, title, ChordPro) into a JSON file."

    def add_arguments(self, parser):
        parser.add_argument("--site", required=True, choices=["StrumSphere", "FrancoUke"])
        parser.add_argument("--origin", help="only this origin, e.g. NBU")
        parser.add_argument("--include-private", action="store_true", help="also songs that are not public")
        parser.add_argument("--out", default="unformatted_songs.json")

    def handle(self, *args, **o):
        qs = Song.objects.filter(site_name=o["site"]).exclude(pk__in=SongFormatting.objects.values("song_id"))
        if not o["include_private"]:
            qs = qs.filter(is_public=True)
        if o["origin"]:
            qs = qs.filter(origin__iexact=o["origin"])
        rows = []
        for s in qs.order_by("songTitle"):
            text = s.songChordPro or ""
            rows.append({"id": s.pk, "title": s.songTitle, "origin": s.origin or "",
                         "chordpro": text, "sha1": sha1_text(text)})
        with open(o["out"], "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        self.stdout.write(self.style.SUCCESS("%d songs written to %s" % (len(rows), o["out"])))
