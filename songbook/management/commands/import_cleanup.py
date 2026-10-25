import re
from collections import Counter
from datetime import date
from pathlib import Path
from django.core.management.base import BaseCommand
from songbook.models import Song
from songbook.management.commands.export_for_cleanup import chord_tokens

HEADER_RE = re.compile(r"^=== SONG (\d+)\b(.*?)===\s*$", re.M)


class Command(BaseCommand):
    help = "Load cleaned batch file back into Song rows (dry run unless --apply)."

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--force", action="store_true", help="apply even if chords differ")

    def handle(self, *args, **o):
        text = Path(o["file"]).read_text(encoding="utf-8")
        heads = list(HEADER_RE.finditer(text))
        done = skipped = 0
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            new = text[h.end():end].strip() + "\n"
            pk = int(h.group(1))
            try:
                song = Song.objects.get(pk=pk)
            except Song.DoesNotExist:
                self.stderr.write(f"#{pk}: not found, skipped")
                skipped += 1
                continue
            if Counter(chord_tokens(song.songChordPro or "")) != Counter(chord_tokens(new)) and not o["force"]:
                self.stderr.write(f"#{pk} {song.songTitle}: chords differ from original, skipped")
                skipped += 1
                continue
            fields = {"songChordPro": new}
            m = re.search(r"revised_on=(\d{4})-(\d\d)-(\d\d)", h.group(2))
            if m:
                fields["revised_on"] = date(*map(int, m.groups()))
            if o["apply"]:
                Song.objects.filter(pk=pk).update(**fields)
            done += 1
            self.stdout.write(f"#{pk} {song.songTitle}: ok")
        verb = "Updated" if o["apply"] else "Would update"
        self.stdout.write(self.style.SUCCESS(f"{verb} {done}, skipped {skipped}"))