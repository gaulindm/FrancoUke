import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from songbook.models import Song

CHORD_RE = re.compile(
    r'^[A-G][#b]?(?:maj|min|m|dim|aug|sus|add|M)?\d*(?:sus\d|add\d)?(?:/[A-G][#b]?)?$'
)
PAREN_RE = re.compile(r'\(.*?\)')


def strip_parens(line):
    return PAREN_RE.sub(lambda m: ' ' * len(m.group()), line)


def is_chord_line(line):
    tokens = strip_parens(line).split()
    return bool(tokens) and all(CHORD_RE.match(t) for t in tokens)


def merge(chord_line, lyric):
    chords = [(m.start(), m.group()) for m in re.finditer(r'\S+', strip_parens(chord_line))]
    out, pos = '', 0
    for start, chord in chords:
        if start >= len(lyric):
            out += lyric[pos:]
            pos = len(lyric)
            if out and not out.endswith((' ', ']')):
                out += ' '
            out += f'[{chord}]'
        else:
            out += lyric[pos:start] + f'[{chord}]'
            pos = start
    return out + lyric[pos:]


def convert(text):
    lines = [l.expandtabs(4).rstrip() for l in text.splitlines()]
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            out.append('')
            i += 1
        elif is_chord_line(line):
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if nxt.strip() and not is_chord_line(nxt):
                out.append(merge(line, nxt))
                i += 2
            else:
                out.append(' '.join(f'[{t}]' for t in strip_parens(line).split()))
                i += 1
            for note in PAREN_RE.findall(line):
                out.append('{c:%s}' % note.strip('()'))
        else:
            out.append(line)
            i += 1
    return '\n'.join(out)


class Command(BaseCommand):
    help = "Convert chords-over-lyrics .txt files to ChordPro, optionally saving them as Songs."

    def add_arguments(self, parser):
        parser.add_argument('source', help='A .txt file or a folder of .txt files')
        parser.add_argument('--out', help='Folder for the .pro files (default: next to the source)')
        parser.add_argument('--artist', default='', help='Optional {artist:} line')
        parser.add_argument('--save', action='store_true',
                            help='Create or update Song records instead of only writing files')
        parser.add_argument('--contributor', help='Username of the contributor (required with --save)')
        parser.add_argument('--origin', default='', help='Song.origin code, e.g. NBU, SOUP, I-UKE')
        parser.add_argument('--site', choices=['FrancoUke', 'StrumSphere'], default=None,
                            help='Song.site_name. Omit to leave the song hidden from all platforms.')

    def handle(self, *args, **opts):
        src = Path(opts['source'])
        if src.is_dir():
            files = sorted(src.glob('*.txt'))
        elif src.is_file():
            files = [src]
        else:
            raise CommandError(f'Not found: {src}')
        if not files:
            raise CommandError('No .txt files found.')

        contributor = None
        if opts['save']:
            if not opts['contributor']:
                raise CommandError('--save requires --contributor <username>')
            User = get_user_model()
            try:
                contributor = User.objects.get(username=opts['contributor'])
            except User.DoesNotExist:
                raise CommandError(f"No user named {opts['contributor']!r}")

        # Write files unless we're saving to the database with no --out folder
        write_files = bool(opts['out']) or not opts['save']
        out_dir = Path(opts['out']) if opts['out'] else None
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            title = f.stem.replace('_', ' ').title()
            body = convert(f.read_text(encoding='utf-8', errors='replace'))
            header = f'{{title: {title}}}\n'
            if opts['artist']:
                header += f'{{artist: {opts["artist"]}}}\n'
            chordpro = header + '\n' + body + '\n'

            if write_files:
                target = (out_dir or f.parent) / f'{f.stem}.pro'
                target.write_text(chordpro, encoding='utf-8')
                self.stdout.write(f'{f.name} -> {target}')

            if opts['save']:
                song = Song.objects.filter(songTitle=title, origin=opts['origin']).first()
                if song:
                    song.songChordPro = chordpro
                    verb = 'updated'
                else:
                    song = Song(
                        songTitle=title,
                        songChordPro=chordpro,
                        contributor=contributor,
                        origin=opts['origin'],
                        site_name=opts['site'],
                    )
                    verb = 'created'
                song.save()
                self.stdout.write(self.style.SUCCESS(
                    f'{verb} Song #{song.pk}: {song.songTitle} (key {song.effective_key}, '
                    f'site {song.site_name or "hidden"})'
                ))