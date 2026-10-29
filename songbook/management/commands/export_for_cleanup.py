import re
from pathlib import Path
from django.core.management.base import BaseCommand
from songbook.models import Song, SongFormatting
from songbook.views.song_display_views import is_valid_chord

NO_ORIGIN = "none"

CHORD = r"(?:[A-G][#b]?(?:maj|min|dim|aug|sus|add|m|M|o|\+)?\d*(?:sus\d?|add\d+)?(?:/[A-G][#b]?)?)"
CHORD_RE = re.compile(CHORD)


def chord_tokens(text):
    """Used by import_cleanup to check that no chord was changed."""
    out = []
    for tok in re.findall(r"\[([^\]]+)\]", text):
        for part in re.split(r"\s*-\s*", tok.strip()):
            part = part.rstrip("/")
            if CHORD_RE.fullmatch(part):
                out.append(part)
    return out


def chord_count(chords_used):
    return len({c.strip() for c in (chords_used or "").split(",") if is_valid_chord(c.strip())})

def chord_bucket(chords_used):
    count = len({c.strip() for c in (chords_used or "").split(",") if is_valid_chord(c.strip())})
    if count <= 1:
        return "le1"
    if count > 5:
        return "gt5"
    return str(count)


class Command(BaseCommand):
    help = "Write the songs from the 'songs to format' list into numbered batch files."

    def add_arguments(self, parser):
        parser.add_argument("--site", required=True, choices=["StrumSphere", "FrancoUke"])
        parser.add_argument("--chord-count", choices=["le1", "2", "3", "4", "5", "gt5"])
        parser.add_argument("--origin", help="e.g. SOUP, or 'none' for songs without origin")
        parser.add_argument("--size", type=int, default=12)
        parser.add_argument("--out", default="cleanup_batches")
        parser.add_argument("--exact-chords", type=int, help="only songs with exactly this many chords, e.g. 10")
        parser.add_argument("--include-private", action="store_true",
                            help="also include songs that are not public")

    def handle(self, *args, **o):
        qs = Song.objects.filter(site_name=o["site"]).exclude(
            pk__in=SongFormatting.objects.values("song_id"))
        if not o["include_private"]:
            qs = qs.filter(is_public=True)

        want_origin = (o["origin"] or "").strip().lower()
        songs = []
        for s in qs.order_by("songTitle"):
            origin_key = (s.origin or "").strip().lower() or NO_ORIGIN
            if want_origin and origin_key != want_origin:
                continue
            if o["chord_count"] and chord_bucket(s.chords_used) != o["chord_count"]:
                continue
            if o["exact_chords"] is not None and chord_count(s.chords_used) != o["exact_chords"]:
                continue
            songs.append(s)

        out = Path(o["out"])
        out.mkdir(exist_ok=True)
        size = o["size"]
        for n, i in enumerate(range(0, len(songs), size), 1):
            chunk = songs[i:i + size]
            body = "\n\n".join(
                f"=== SONG {s.pk} | {s.songTitle} ===\n{(s.songChordPro or '').strip()}" for s in chunk)
            (out / f"batch_{n:02d}.txt").write_text(body + "\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(
            f"{len(songs)} songs -> {-(-len(songs) // size)} batch files in {out}/"))