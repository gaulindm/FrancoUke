# songbook/management/commands/apply_local_chordpro.py           (run on PRODUCTION)
import json
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from songbook.models import Song
from songbook.sync_utils import norm_title, sha1_text


class Command(BaseCommand):
    help = "PRODUCTION: copy the ChordPro found by match_local_chordpro into the production songs (dry run unless --apply)."

    def add_arguments(self, parser):
        parser.add_argument("matches", help="matches.json made on the local machine (or a backup file with --restore)")
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--limit", type=int, help="only the first N songs (try 2 first!)")
        parser.add_argument("--raw", action="store_true",
                            help="write with a raw UPDATE instead of song.save() (skips any save() logic)")
        parser.add_argument("--with-revised", action="store_true", help="also copy the local revised_on date")
        parser.add_argument("--backup", help="where to save the old texts (default: chordpro_backup_<time>.json)")
        parser.add_argument("--restore", action="store_true",
                            help="the file is a backup: put the old texts back")

    def handle(self, *args, **o):
        with open(o["matches"], encoding="utf-8") as f:
            rows = json.load(f)
        if o["restore"]:
            return self.restore(rows, o)
        if o["limit"]:
            rows = rows[:o["limit"]]
        todo, skipped = [], 0
        for r in rows:
            try:
                song = Song.objects.get(pk=r["prod_id"])
            except Song.DoesNotExist:
                self.stderr.write("#%s %s: no longer exists, skipped" % (r["prod_id"], r["prod_title"])); skipped += 1; continue
            if norm_title(song.songTitle) != norm_title(r["prod_title"]):
                self.stderr.write("#%s: title is now %r, expected %r - skipped" % (song.pk, song.songTitle, r["prod_title"])); skipped += 1; continue
            if sha1_text(song.songChordPro) != r["prod_sha1"]:
                self.stderr.write("#%s %s: edited on production since the export - skipped" % (song.pk, song.songTitle)); skipped += 1; continue
            todo.append((song, r))
            old_n = len((song.songChordPro or "").splitlines()); new_n = len(r["chordpro"].splitlines())
            self.stdout.write("#%-6s %-45s lines %d -> %d  (from local #%s)" % (
                song.pk, song.songTitle[:45], old_n, new_n, r["local_id"]))
        if not o["apply"]:
            self.stdout.write(self.style.WARNING("\nDry run: %d would be updated, %d skipped. Add --apply to write." % (len(todo), skipped)))
            return
        backup = o["backup"] or "chordpro_backup_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(backup, "w", encoding="utf-8") as f:     # backup FIRST
            json.dump([{"prod_id": s.pk, "prod_title": s.songTitle, "chordpro": s.songChordPro or ""} for s, _ in todo],
                      f, ensure_ascii=False, indent=1)
        with transaction.atomic():
            for song, r in todo:
                self.write_song(song, r["chordpro"], r.get("revised_on") if o["with_revised"] else "", o["raw"])
        self.stdout.write(self.style.SUCCESS("Updated %d songs, skipped %d. Old texts saved in %s" % (len(todo), skipped, backup)))

    def write_song(self, song, text, revised, raw):
        fields = {"songChordPro": text}
        if revised:
            fields["revised_on"] = revised
        if raw:
            Song.objects.filter(pk=song.pk).update(**fields)
        else:
            for k, v in fields.items():
                setattr(song, k, v)
            song.save()

    def restore(self, rows, o):
        n = 0
        with transaction.atomic():
            for r in rows:
                try:
                    song = Song.objects.get(pk=r["prod_id"])
                except Song.DoesNotExist:
                    continue
                n += 1
                self.stdout.write("#%-6s %s" % (song.pk, song.songTitle[:50]))
                if o["apply"]:
                    self.write_song(song, r["chordpro"], "", o["raw"])
        self.stdout.write(self.style.SUCCESS(("Restored %d songs." if o["apply"] else "Dry run: %d songs would be restored.") % n))
