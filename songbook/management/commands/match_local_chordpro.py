# songbook/management/commands/match_local_chordpro.py           (run on your LOCAL machine)
import json
from collections import Counter
from django.core.management.base import BaseCommand
from songbook.models import Song, SongFormatting
from songbook.sync_utils import match_songs

LABELS = {
    "ok": "will be copied",
    "identical": "same text already (nothing to copy)",
    "no_local_match": "no song with this title locally",
    "local_not_fixed": "found locally but not formatted there (only with --only-formatted-local)",
    "low_similarity": "title matches but the lyrics are too different",
    "ambiguous": "several local songs fit; cannot choose",
    "chords_differ": "chords differ between the two versions",
}


class Command(BaseCommand):
    help = "LOCAL: for each song in the production list, find the already-formatted local song (matched by title)."

    def add_arguments(self, parser):
        parser.add_argument("input", help="unformatted_songs.json from the production server")
        parser.add_argument("--site", required=True, choices=["StrumSphere", "FrancoUke"])
        parser.add_argument("--any-site", action="store_true", help="search local songs of every site")
        parser.add_argument("--only-formatted-local", action="store_true",
                            help="only use local songs that have formatting rows (default: any local song)")
        parser.add_argument("--allow-chord-diff", action="store_true",
                            help="copy even when the set of chords differs")
        parser.add_argument("--min-similarity", type=float, default=0.75)
        parser.add_argument("--out", default="matches.json")
        parser.add_argument("--report", default="match_report.txt")

    def handle(self, *args, **o):
        with open(o["input"], encoding="utf-8") as f:
            prod = json.load(f)
        qs = Song.objects.all()
        if not o["any_site"]:
            qs = qs.filter(site_name=o["site"])
        fixed = set(SongFormatting.objects.values_list("song_id", flat=True))
        local = [{"id": s.pk, "title": s.songTitle, "origin": s.origin or "",
                  "chordpro": s.songChordPro or "", "formatted": s.pk in fixed,
                  "revised_on": str(s.revised_on) if getattr(s, "revised_on", None) else ""}
                 for s in qs]
        results = match_songs(prod, local, allow_unformatted=not o["only_formatted_local"],
                              min_sim=o["min_similarity"], allow_chord_diff=o["allow_chord_diff"])
        ok = [r for r in results if r["status"] == "ok"]
        with open(o["out"], "w", encoding="utf-8") as f:
            json.dump(ok, f, ensure_ascii=False, indent=1)
        lines = []
        for status in LABELS:
            group = [r for r in results if r["status"] == status]
            if not group:
                continue
            lines.append("\n== %s: %s (%d)" % (status, LABELS[status], len(group)))
            for r in group:
                extra = []
                if r["local_id"]:
                    extra.append("local #%s %r" % (r["local_id"], r["local_title"]))
                if r["similarity"] is not None:
                    extra.append("similarity %.2f" % r["similarity"])
                if r["note"]:
                    extra.append(r["note"])
                lines.append("  prod #%-6s %-45s %s" % (r["prod_id"], r["prod_title"][:45], " | ".join(extra)))
        with open(o["report"], "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        counts = Counter(r["status"] for r in results)
        self.stdout.write("Production songs checked: %d" % len(prod))
        for status, label in LABELS.items():
            if counts.get(status):
                self.stdout.write("  %-16s %4d  %s" % (status, counts[status], label))
        self.stdout.write(self.style.SUCCESS("%d songs ready to copy -> %s (details in %s)" % (len(ok), o["out"], o["report"])))