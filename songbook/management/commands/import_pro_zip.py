"""
import_pro_zip -- import a zip file of ChordPro (.pro) files as Song rows.

Like clean_artist_field.py, this is a DRY RUN unless you add --apply.

    # 1. See what WOULD happen (changes nothing):
    python manage.py import_pro_zip SOUP_SONGS.zip --origin SOUP --contributor daniel

    # 2. When the report looks right, do it for real:
    python manage.py import_pro_zip SOUP_SONGS.zip --origin SOUP --contributor daniel --apply

    python manage.py import_pro_zip playlist4.zip --origin I-Ukes --contributor francoukedg --apply
    

Optional:
    --site FrancoUke     make the songs visible on that site right away.
                         (Left off, site_name stays empty, which HIDES the songs
                         from every platform until you set it, e.g. with an admin action.)
    -v 2                 also list every title that was tidied up.

Safe to re-run: a song whose title already exists with the same origin is skipped.
"""
import difflib
import re
import zipfile

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from songbook.models import Song

# Which files inside the zip count as songs. Everything else (.lst setlists,
# .pdf copies, folders) is ignored and counted in the report.
SONG_EXTENSIONS = (".pro", ".cho", ".chordpro")

# --- Title tidying -----------------------------------------------------------
# The SOUP files came from a desktop program, so titles carry leftovers:
#   "137   MY LITTLE RUNAWAY"              <- jam-list number
#   "C09: HAVE YOURSELF A MERRY"           <- Christmas-list number
#   "C11: LITTLE SAINT NICK   4/4  Key of Am"  <- time/key typed into the title
JAM_NUMBER = re.compile(r"^\s*\d{3}\s+")          # exactly 3 digits + space ("9 to 5" is safe)
XMAS_NUMBER = re.compile(r"^\s*C\d{1,2}:\s*")     # C09:  C22:
TRAILING_JUNK = re.compile(r"\s+(?:\d/\d|Key\s+of)\b.*$", re.IGNORECASE)

# The first {title: ...} or {t: ...} directive in the song text.
TITLE_TAG = re.compile(r"\{(?:title|t)\s*:[^}]*\}", re.IGNORECASE)

# A "real" chord in square brackets, e.g. [C] [F#m7] [G/B]. Files without one
# are notes or blank templates, not songs.
HAS_CHORD = re.compile(r"\[[A-G][^\]]*\]")


# Older copies less alike than this are reported as "different arrangements".
DIFFERENT_BELOW = 0.60


def short(name):
    """A file name safe to print (some names contain line breaks or are very long)."""
    return re.sub(r"\s+", " ", name).strip()[:80]


def clean_title(raw):
    """Turn a messy title into the title we actually want to show."""
    title = XMAS_NUMBER.sub("", JAM_NUMBER.sub("", raw))
    title = TRAILING_JUNK.sub("", title)
    return re.sub(r"\s+", " ", title).strip()


def title_from_filename(filename):
    """Fallback when a file has an empty {title:}. Uses the file name."""
    stem = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    # Some zip tools write curly quotes as '#U2019'; turn them back into characters.
    stem = re.sub(r"#U([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), stem)
    return clean_title(stem)


def read_text(raw_bytes):
    """Bytes -> str with Unix line endings (\\n)."""
    try:
        text = raw_bytes.decode("utf-8-sig")      # utf-8-sig quietly drops a BOM
    except UnicodeDecodeError:
        text = raw_bytes.decode("cp1252")         # old Windows files
    # parse_song_data() splits paragraphs on "\n\n", so Windows "\r\n" line
    # endings would make blank lines invisible to it. Normalise first.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def set_title_tag(text, title):
    """Make the song text's own {title:} agree with the cleaned title."""
    new_tag = "{title:%s}" % title
    if TITLE_TAG.search(text):
        # lambda so backslashes/& in a title are never treated as regex escapes
        return TITLE_TAG.sub(lambda m: new_tag, text, count=1)
    return new_tag + "\n" + text


def fingerprint(text):
    """Text with the title line and all spacing/case removed, for duplicate checks."""
    body = TITLE_TAG.sub("", text, count=1)
    return re.sub(r"\s+", " ", body).strip().lower()


class Command(BaseCommand):
    help = "Import the ChordPro (.pro) files in a zip file as Songs (dry run unless --apply)."

    def add_arguments(self, parser):
        parser.add_argument("zipfile", help="Path to the .zip file")
        parser.add_argument("--origin", required=True,
                            help="Short code stored in Song.origin, e.g. SOUP (max 20 characters)")
        parser.add_argument("--contributor", required=True,
                            help="Username that will own the imported songs")
        parser.add_argument("--site", choices=[c[0] for c in Song.SITE_CHOICES], default=None,
                            help="Song.site_name. Omit to leave empty (songs hidden until set).")
        parser.add_argument("--apply", action="store_true",
                            help="Actually write to the database. Without this it is a dry run.")

    # ------------------------------------------------------------------ main
    def handle(self, *args, **opts):
        origin = opts["origin"].strip()
        if not origin or len(origin) > Song._meta.get_field("origin").max_length:
            raise CommandError("--origin must be 1-%d characters." %
                               Song._meta.get_field("origin").max_length)

        User = get_user_model()
        try:
            contributor = User.objects.get(username=opts["contributor"])
        except User.DoesNotExist:
            raise CommandError("No user with username '%s'." % opts["contributor"])

        try:
            archive = zipfile.ZipFile(opts["zipfile"])
        except (FileNotFoundError, zipfile.BadZipFile) as exc:
            raise CommandError("Cannot open zip file: %s" % exc)

        apply_changes = opts["apply"]
        verbose = opts["verbosity"] >= 2

        # ---- Pass 1a: read every song file in the zip ----
        candidates = []           # one dict per usable file
        skipped_not_song = {}     # extension -> count
        skipped_no_chords = []

        for info in sorted(archive.infolist(), key=lambda i: i.filename):
            name = info.filename
            if info.is_dir() or "__MACOSX" in name:
                continue
            if not name.lower().endswith(SONG_EXTENSIONS):
                ext = name.rsplit(".", 1)[-1].lower() if "." in name else "(none)"
                skipped_not_song[ext] = skipped_not_song.get(ext, 0) + 1
                continue

            text = read_text(archive.read(info)).strip()
            if not HAS_CHORD.search(text):
                skipped_no_chords.append(name)
                continue

            m = TITLE_TAG.search(text)
            raw_title = re.sub(r"^\{(?:title|t)\s*:|\}$", "", m.group(0), flags=re.I).strip() if m else ""
            title = clean_title(raw_title) or title_from_filename(name)
            text = set_title_tag(text, title) + "\n"
            candidates.append({
                "name": name, "date": info.date_time, "raw_title": raw_title or "(empty)",
                "title": title, "text": text, "fp": fingerprint(text),
            })

        # ---- Pass 1b: several files can end up with the same title once tidied
        # ("044   AHEAD BY A CENTURY" and "AHEAD BY A CENTURY"). The NEWEST file
        # (by the date stored in the zip) wins; ties go to the first file name.
        groups = {}
        for c in candidates:
            groups.setdefault(c["title"].lower(), []).append(c)

        to_create = []            # winners that are not in the database yet
        title_changes = []        # (original, cleaned) for songs we import
        skipped_exact_dupes = []  # (title, file)
        skipped_older = []        # (title, kept_file, skipped_file, similarity)
        skipped_existing = []
        also_other_origin = []    # informational only

        for group in groups.values():
            winner = max(group, key=lambda c: c["date"])     # max() keeps the first on a tie
            for other in group:
                if other is winner:
                    continue
                if other["fp"] == winner["fp"]:
                    skipped_exact_dupes.append((winner["title"], other["name"]))
                else:
                    ratio = difflib.SequenceMatcher(None, winner["text"], other["text"]).ratio()
                    skipped_older.append((winner["title"], winner["name"], other["name"], ratio))

            title = winner["title"]
            if Song.objects.filter(songTitle__iexact=title, origin=origin).exists():
                skipped_existing.append(title)
                continue
            if Song.objects.filter(songTitle__iexact=title).exclude(origin=origin).exists():
                also_other_origin.append(title)
            if winner["title"] != winner["raw_title"]:
                title_changes.append((winner["raw_title"], title))
            to_create.append((title, winner["text"], winner["name"]))

        # ---- Pass 2: write (only with --apply) ----
        created, failed = 0, []
        if apply_changes:
            for title, text, name in to_create:
                try:
                    with transaction.atomic():      # one bad song can't spoil the rest
                        Song(songTitle=title, songChordPro=text, contributor=contributor,
                             origin=origin, site_name=opts["site"]).save()
                    created += 1
                except Exception as exc:            # report it and keep going
                    failed.append((title, name, exc))

        # ---- Report ----
        w = self.stdout.write
        w(self.style.MIGRATE_HEADING(
            "%s  (origin=%s, contributor=%s, site=%s)" %
            ("APPLYING" if apply_changes else "DRY RUN - nothing is saved",
             origin, contributor.username, opts["site"] or "none/hidden")))
        w("")
        w("Songs %s: %d" % ("created" if apply_changes else "that would be created",
                            created if apply_changes else len(to_create)))
        w("Titles tidied (of the songs above): %d" % len(title_changes))
        w("Skipped - identical to a newer file in the zip: %d" % len(skipped_exact_dupes))
        w("Skipped - older copy of a song (same title, edited since): %d" % len(skipped_older))
        w("Skipped - already in the database with origin %s: %d" % (origin, len(skipped_existing)))
        w("Skipped - no chords in file: %d" % len(skipped_no_chords))
        if skipped_not_song:
            w("Ignored - not song files: %s" % ", ".join(
                "%d x .%s" % (n, e) for e, n in sorted(skipped_not_song.items())))
        if also_other_origin:
            w("Note - %d title(s) also exist under another origin (imported anyway; "
              "origin is what tells versions apart)." % len(also_other_origin))
        if not opts["site"]:
            w(self.style.WARNING("Note - no --site given: imported songs will be HIDDEN "
                                 "until site_name is set."))

        different = [v for v in skipped_older if v[3] < DIFFERENT_BELOW]
        if different:
            w("")
            w("Older copies that look like a genuinely DIFFERENT arrangement (<%d%% alike) - "
              "NOT imported, you may want both:" % round(DIFFERENT_BELOW * 100))
            for title, kept, skipped, ratio in sorted(different, key=lambda v: v[3]):
                w("  %s  [%d%% alike]\n      imported: %s\n      left out: %s" %
                  (title, round(ratio * 100), short(kept), short(skipped)))
        if verbose and skipped_older:
            w("")
            w("All older copies left out:")
            for title, kept, skipped, ratio in skipped_older:
                w("  %s  [%d%% alike]  %s" % (title, round(ratio * 100), short(skipped)))
        if skipped_no_chords:
            w("")
            w("No chords found:")
            for name in skipped_no_chords:
                w("  " + short(name))
        if verbose and title_changes:
            w("")
            w("Title changes:")
            for before, after in title_changes:
                w("  %r  ->  %r" % (before, after))
        if failed:
            w("")
            w(self.style.ERROR("FAILED (%d):" % len(failed)))
            for title, name, exc in failed:
                w("  %s (%s): %s" % (title, name, exc))
        if not apply_changes:
            w("")
            w("Re-run with --apply to import.")