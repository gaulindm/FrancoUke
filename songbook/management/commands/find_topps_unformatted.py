"""
songbook/management/commands/find_topps_unformatted.py

Lists songs that are NOT formatted yet and carry the acknowledgement
"Contribution of Heather J. Topps of the North Bay Ukulele Club".

Dry run by default (just reports). Add --apply with --set-origin NBU to
set the origin on the songs that don't have it.

Usage:
    python manage.py find_topps_unformatted
    python manage.py find_topps_unformatted --csv topps_unformatted.csv
    python manage.py find_topps_unformatted --set-origin NBU --apply
"""
import csv
import re

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from songbook.models import Song

try:
    from songbook.models import SongFormatting
except ImportError:  # adjust if SongFormatting lives elsewhere
    SongFormatting = None

# 🔧 TUNE
ACK_TEXT = "Contribution of Heather J. Topps of the North Bay Ukulele Club"
ACK_FIELD = "acknowledgement"   # Song field name, if there is one
CHORDPRO_FIELD = "songChordPro"  # fallback: search the {acknowledgement:} tag


class Command(BaseCommand):
    help = "Find unformatted songs acknowledging Heather J. Topps (NBU)."

    def add_arguments(self, parser):
        parser.add_argument("--csv", help="Also write results to this CSV file")
        parser.add_argument("--set-origin", help="Origin code to set, e.g. NBU")
        parser.add_argument("--apply", action="store_true",
                            help="Actually save the origin change (default is dry run)")

    # ---- helpers -------------------------------------------------------
    def _ack_filter(self):
        field_names = {f.name for f in Song._meta.get_fields()}
        if ACK_FIELD in field_names:
            self.stdout.write(f"Matching on Song.{ACK_FIELD}")
            return Q(**{f"{ACK_FIELD}__icontains": ACK_TEXT})
        if CHORDPRO_FIELD in field_names:
            self.stdout.write(f"No Song.{ACK_FIELD} field; searching {CHORDPRO_FIELD} text")
            return Q(**{f"{CHORDPRO_FIELD}__icontains": ACK_TEXT})
        raise CommandError("Can't find an acknowledgement or ChordPro field on Song.")

    def _unformatted_filter(self):
        """Songs with no SongFormatting row."""
        if SongFormatting is None:
            raise CommandError("Couldn't import SongFormatting - fix the import at the top.")
        for f in SongFormatting._meta.get_fields():
            if getattr(f, "related_model", None) is Song and (f.many_to_one or f.one_to_one):
                rel = f.remote_field.get_accessor_name()
                query_name = f.related_query_name()
                self.stdout.write(f"Unformatted = no SongFormatting row (via '{query_name}')")
                return Q(**{f"{query_name}__isnull": True})
        raise CommandError("SongFormatting has no ForeignKey to Song.")

    # ---- main ----------------------------------------------------------
    def handle(self, *args, **opts):
        qs = (Song.objects
              .filter(self._ack_filter())
              .filter(self._unformatted_filter())
              .distinct()
              .order_by("songTitle"))

        total = qs.count()
        no_nbu = qs.exclude(origin__iexact="NBU")
        self.stdout.write(self.style.SUCCESS(
            f"\n{total} unformatted songs with the Topps acknowledgement "
            f"({no_nbu.count()} without NBU origin)\n"))

        rows = []
        for s in qs:
            rows.append([s.pk, s.songTitle, getattr(s, "origin", "") or ""])
            self.stdout.write(f"  {s.pk:>6}  {s.songTitle[:50]:<50}  origin={s.origin or '-'}")

        if opts["csv"]:
            with open(opts["csv"], "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["id", "title", "origin"])
                w.writerows(rows)
            self.stdout.write(f"\nWrote {opts['csv']}")

        if opts["set_origin"]:
            code = opts["set_origin"]
            ids = list(no_nbu.values_list("pk", flat=True).distinct())
            if opts["apply"]:
                # .update() skips Song.save(), so derived fields stay untouched
                n = Song.objects.filter(pk__in=ids).update(origin=code)
                self.stdout.write(self.style.SUCCESS(f"Set origin={code} on {n} songs."))
            else:
                self.stdout.write(self.style.WARNING(
                    f"DRY RUN: would set origin={code} on {len(ids)} songs. Add --apply."))