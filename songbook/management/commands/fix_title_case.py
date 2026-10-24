import re
from django.core.management.base import BaseCommand
from songbook.models import Song

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "in", "nor",
    "of", "on", "or", "the", "to", "up", "with",
}
KEEP_UPPER = {"USA", "DJ", "TV", "OK", "UK", "BBQ"}  # add your own

# Words (including accented letters) with apostrophes: don't, I'm, rock'n'roll, l'été
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")

# {title: ...} or {t: ...} on a line of its own
TITLE_LINE = re.compile(
    r"^([ \t]*\{(?:title|t):[ \t]*)([^}]*?)([ \t]*\}[ \t]*)$",
    re.IGNORECASE | re.MULTILINE,
)


def smart_title(text):
    first = True

    def fix(match):
        nonlocal first
        word = match.group(0)
        is_first, first = first, False
        if word.upper() in KEEP_UPPER:
            return word.upper()
        if not is_first and word.lower() in SMALL_WORDS:
            return word.lower()
        return word[:1].upper() + word[1:].lower()

    return WORD.sub(fix, text)


def fix_title_line(body):
    """Re-case the {title:} line, but only if that line is all caps."""
    def repl(m):
        value = m.group(2)
        if value.isupper():
            value = smart_title(value)
        return m.group(1) + value + m.group(3)

    return TITLE_LINE.sub(repl, body, count=1)


class Command(BaseCommand):
    help = "Convert ALL CAPS songTitle values and {title:} lines to Title Case"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true",
                            help="Actually save changes (default is a dry run)")

    def handle(self, *args, **opts):
        changed = 0
        for song in Song.objects.all().iterator():
            old_title = song.songTitle or ""
            old_body = song.songChordPro or ""

            new_title = smart_title(old_title) if old_title.isupper() else old_title
            new_body = fix_title_line(old_body)

            updates = {}
            if new_title != old_title:
                updates["songTitle"] = new_title
            if new_body != old_body:
                updates["songChordPro"] = new_body
            if not updates:
                continue

            self.stdout.write(
                f"{old_title}  ->  {new_title}  [{', '.join(updates)}]"
            )
            if opts["apply"]:
                # .update() skips save(), so date_posted is not bumped
                Song.objects.filter(pk=song.pk).update(**updates)
            changed += 1

        mode = "Updated" if opts["apply"] else "Would update"
        self.stdout.write(self.style.SUCCESS(f"{mode} {changed} songs"))