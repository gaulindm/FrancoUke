"""
songfix.py -- clean up songs imported from PDFs and add section tags.

    python songfix.py  batch_NN.txt  spec_batchNN.py  batch_NN_clean.txt
    python songfix.py  batch_NN.txt  batch_NN_clean.txt        (automatic clean-up only, no section tags)

1. Cleans the header junk, restores lyric words eaten by the importer,
   repairs damaged brackets, turns [echoes] into (echoes), etc.
2. Wraps sections ({sov}/{eov} ...) using the line ranges in the spec file.
3. Checks every song: no chord may go missing (chords ADDED by bracket
   repairs are listed), and warns if lyric words disappeared.
Nothing is written to the database; load the result with import_cleanup.
"""
import re, datetime
from collections import Counter

CHORD = r"\*?[A-G][#b]?(?:maj|min|dim|aug|sus|add|m|M|o|\+)?\d*(?:[b#+]\d+)*(?:sus\d?|add\d+)?(?:/(?:[A-G][#b]?|\d))?\*?/*"
CH_GROUP = re.compile(rf"^{CHORD}(?:\s*-\s*{CHORD})*$")
NC = re.compile(r"^N\.?C\.?\s*/*$")
def is_chordtok(t):
    t = t.strip()
    return bool(CH_GROUP.match(t) or NC.match(t))

def chord_list(text):
    out = []
    for tok in re.findall(r"\[([^\]]+)\]", text):
        for part in re.split(r"\s*-\s*", tok.strip()):
            part = part.rstrip("/")
            if re.fullmatch(CHORD, part):
                out.append(part)
    return out

HEAD_RE = re.compile(r"^=== SONG (\d+) \| (.*?) ===\s*$")
DIR_RE = re.compile(r"^\{([^:}]+):?(.*)\}\s*$")
TAGS = {"soi":"i","sov":"v","soc":"c","sob":"b","soo":"o","sos":"c","sod":"i"}
WORD = {"soi":"intro","sov":"verse","soc":"chorus","sob":"bridge","soo":"outro","sos":"s","sod":"d"}
STD = ["title","artist","youtube","songwriter","capo","year","1stnote","timeSignature"]
DATE_RE = re.compile(r"^(?:\{so[icvbods]\})?\s*\[?\(?([A-Za-z]{3,9}\.? \d{1,2}, \d{4})\)?\]?$")

def parse_date(s):
    s = s.replace("Sept.", "Sep.")
    for f in ("%b. %d, %Y","%b %d, %Y","%B %d, %Y"):
        try: return datetime.datetime.strptime(s, f).date()
        except ValueError: pass

def norm(s):
    s = re.sub(r"\[[^\]]*\]", "", s)
    return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("’","'")).split()

def parse_batch(path):
    raw = re.sub(r"[\uf000-\uf8ff\u200b\ufeff]", "", open(path, encoding="utf-8").read()).replace("\r\n","\n").replace("\r","\n")
    songs, cur = [], None
    for line in raw.split("\n"):
        m = HEAD_RE.match(line)
        if m:
            cur = {"id": int(m.group(1)), "title_hdr": m.group(2), "lines": []}
            songs.append(cur)
        elif cur is not None:
            cur["lines"].append(line.rstrip())
    return songs

def capfirst(s):
    s = s.strip()
    return s[:1].upper() + s[1:]

def auto_clean(song):
    lines = list(song["lines"])
    while lines and not lines[-1].strip(): lines.pop()
    # directive block
    dirs, i = {}, 0
    order = []
    while i < len(lines) and (not lines[i].strip() or (DIR_RE.match(lines[i].strip()) and not re.match(r"^\{(so|eo)[icvbods]\}", lines[i].strip()))):
        m = DIR_RE.match(lines[i].strip())
        if m and re.match(r"^(so|eo)[icvbods]$", m.group(1).strip()):
            break
        if m:
            k, v = m.group(1).strip(), m.group(2).strip()
            if k == "t": k = "title"
            if k not in order: order.append(k)
            dirs[k] = v if (v or k not in dirs) else dirs[k]
            if v: dirs[k] = v
        i += 1
    body = lines[i:]
    notes, comments = [], []
    song["orig_body_text"] = "\n".join(song["lines"])
    # trailing date
    rev = None
    if body:
        m = DATE_RE.match(body[-1].strip())
        if m and parse_date(m.group(1)):
            rev = parse_date(m.group(1)); body.pop()
    while body and not body[-1].strip(): body.pop()
    # header zone
    first = None
    for j, l in enumerate(body):
        if any(is_chordtok(t) and not NC.match(t.strip()) for t in re.findall(r"\[([^\]]*)\]", l)):
            first = j; break
    zone_end = first if (first is not None and first <= 8) else 0
    zone, rest = body[:zone_end], body[zone_end:]
    title_n = norm(dirs.get("title",""))
    keep = []
    for l in zone:
        l0 = l
        m = re.search(r"First vocal note\s*=\s*([A-G][#b]?m?)", l)
        if m:
            if not dirs.get("1stnote"): dirs["1stnote"] = m.group(1)
            l = l.replace(m.group(0), "")
        m = re.match(r"^\s*(\d+/\d+|Cut time)\b", l)
        if m:
            if not dirs.get("timeSignature"): dirs["timeSignature"] = m.group(1)
            l = l.replace(m.group(1), "", 1)
        for tok in re.findall(r"\[([^\]]*)\]", l):
            t = tok.strip()
            if is_chordtok(t): continue
            low = t.lower()
            if re.fullmatch(r"/\s*=\s*one strum", low):
                comments.append("/ = one strum")
            elif re.match(r"capo on fret (\d+)", low):
                n = re.match(r"capo on fret (\d+)", low).group(1)
                if not dirs.get("capo"): dirs["capo"] = n
                comments.append(capfirst(t))
            elif re.fullmatch(r"\d{4}", t):
                if not dirs.get("year"): dirs["year"] = t
            elif low.startswith("page "):
                pass
            elif norm(t) == norm(dirs.get("songwriter","")) or norm(t) == norm(dirs.get("artist","")):
                pass
            elif low.endswith(" recording") and not low.startswith(("key","based")) and norm(t[:-10]) == norm(dirs.get("artist","")):
                pass
            else:
                comments.append(capfirst(t)); notes.append(f"header token -> comment: {t}")
            l = l.replace(f"[{tok}]", "")
        l = re.sub(r"\s+", " ", l).strip()
        if not l: continue
        ln = norm(l)
        if ln and all(w in title_n or w == "the" for w in ln): continue
        keep.append(l); notes.append(f"kept header-zone line: {l}")
    body = keep + rest
    # body processing
    out = []
    def addline(text, hint=""):
        out.append({"text": text, "hint": hint})
    for l in body:
        l = l.strip("\u200b")
        hint = ""
        m = re.match(r"^\{(eo[icvbods])\}\s*$", l)
        if m: continue
        if re.match(r"^\{c:\s*\}\s*$", l): continue
        m = re.match(r"^\{c:\s*(.*?)\s*\}\s*$", l)
        if m and not re.match(r"^\{so", l):
            addline("{c:" + capfirst(m.group(1)) + "}"); continue
        if re.match(r"^\[page \d+\]", l.strip()):
            if out and out[-1]["text"] and norm(out[-1]["text"]) and all(w in title_n or w=="the" for w in norm(out[-1]["text"])):
                out.pop()
            continue
        # pre-chorus
        m = re.match(r"^Pre-\{soc\}(.*)$", l)
        if m:
            addline("{c:Pre-chorus}"); l = m.group(1)
        # leading tag
        m = re.match(r"^\{(so[icvbods])\}\s*(\d+:)?\s*(.*)$", l)
        if m:
            hint = m.group(1)[2:] + (m.group(2) or "")
            l = m.group(3)
        # mid-line tags -> restore word
        def sub(mm):
            w = WORD[mm.group(1)]
            before = re.sub(r"\[[^\]]*\]", "", l[:mm.start()])
            if not before.strip() or re.search(r"[.!?]\s*$", before): w = w.capitalize()
            after = l[mm.end():]
            sp = "" if (not after or after[0] in " .,;:!?)-") else " "
            notes.append(f"restored word '{w}' in: {l[:60]}")
            return w + sp
        l = re.sub(r"\{(so[icvbods])\}", sub, l)
        # damaged brackets
        l, n = re.subn(r"\[([^\]\[(]*)\(([A-G][#b]?[A-Za-z0-9+/*]*)\]", r"(\1[\2]", l)
        if n: notes.append(f"repaired {n} damaged bracket(s): {l[:50]}")
        # count cues
        l = re.sub(r"\s*\[(\d(?:\s*,\s*\d)+)\]", lambda mm: " {c:(" + re.sub(r"\D","",mm.group(1)) + ")}", l)
        # trailing markers
        tail = []
        for pat, name in ((r"\s*\[repeat (?:&|and) fade\]", "Repeat and fade"), (r"\s*\[fade\]", "Fade")):
            if re.search(pat, l):
                l = re.sub(pat, "", l); tail.append("{c:%s}" % name)
        # interlude lines
        m = re.match(r"^(Interlude(?: \d+)?|Instrumental(?:/Kazoo)?):\s*(.*)$", l)
        if m:
            addline("{c:%s}" % m.group(1)); l = m.group(2)
            if not l: continue
        # remaining non-chord brackets -> parentheses
        def br(mm):
            t = mm.group(1)
            return mm.group(0) if (is_chordtok(t) or re.fullmatch(r"[\s/\\x\-\d]*", t, re.I)) else "(" + t + ")"
        l = re.sub(r"\[([^\]]*)\]", br, l)
        l = re.sub(r"\s+$", "", l)
        addline(l, hint)
        for t in tail: addline(t)
    song["dirs"] = dirs; song["order"] = order
    song["comments"] = comments; song["rev"] = rev
    song["body"] = out; song["notes"] = notes
    return song

def show(song):
    print(f"##### {song['id']} | {song['title_hdr']} | rev={song['rev']}")
    print("dirs:", {k:v for k,v in song['dirs'].items()})
    print("comments:", song['comments'])
    for n in song['notes']: print("  note:", n)
    for k, b in enumerate(song['body']):
        h = f"«{b['hint']}» " if b['hint'] else ""
        print(f"{k:3d} {h}{b['text']}")
    print()


# ---------------------------------------------------------------------------
# Building the cleaned song from the automatic clean-up + a spec
# ---------------------------------------------------------------------------
CLOSE = {"v": "eov", "c": "eoc", "b": "eob", "i": "eoi", "o": "eoo"}
OPEN = {"v": "sov", "c": "soc", "b": "sob", "i": "soi", "o": "soo"}
DROP_EMPTY = {"album", "recording", "tempo", "key", "time", "metronome"}

def build(song, sp):
    d = dict(song["dirs"]); d.update(sp.get("dir", {}))
    comments = sp.get("comments", song["comments"])
    rev = sp.get("rev", song["rev"])
    head = "=== SONG %d | %s%s ===" % (song["id"], song["title_hdr"],
                                      (" | revised_on=%s" % rev) if rev else "")
    out = [head]
    for k in STD:
        out.append("{%s:%s}" % (k, d.get(k, "")))
    for k, v in d.items():
        if k not in STD and v and k not in ("soc", "sov", "sob", "soi", "soo"):
            out.append("{%s:%s}" % (k, v))
    out.append("")
    seen = []
    for c in comments:
        if c not in seen:
            seen.append(c); out.append("{c:%s}" % c)
    if seen: out.append("")
    body = song["body"]
    drop = set(sp.get("drop", [])); repl = sp.get("repl", {}); before = sp.get("before", {})
    starts = {a: (b, t) for a, b, t in sp.get("sections", [])}
    def blank():
        if out and out[-1] != "": out.append("")
    i = 0
    while i < len(body):
        if i in drop:
            i += 1; continue
        for line in before.get(i, []):
            if i in starts: blank()
            out.append(line)
        if i in starts:
            end, t = starts[i]
            blank(); out.append("{%s}" % OPEN[t])
            for j in range(i, end + 1):
                if j in drop: continue
                txt = repl.get(j, body[j]["text"])
                if txt.strip(): out.append(txt)
            out.append("{%s}" % CLOSE[t]); out.append("")
            i = end + 1
        else:
            txt = repl.get(i, body[i]["text"])
            if txt.strip(): out.append(txt)
            i += 1
    for line in sp.get("append", []):
        blank(); out.append(line)
    while out and out[-1] == "": out.pop()
    return "\n".join(out) + "\n"

def lyric_words(text):
    t = re.sub(r"\[[^\]]*\]", " ", text)
    t = re.sub(r"\{[^}]*\}", " ", t)
    return Counter(re.sub(r"[^a-z0-9 ']", " ", t.lower().replace("’", "'")).split())

def verify(song, built):
    body = built.split("\n", 1)[1]
    orig = chord_list(song["orig_body_text"])
    new = chord_list(body)
    missing = Counter(orig) - Counter(new)
    added = Counter(new) - Counter(orig)
    lo, ln = lyric_words(song["orig_body_text"]), lyric_words(body)
    lost = lo - ln
    ign = set()
    for k in ("title", "artist", "songwriter"):
        ign |= set(norm(song["dirs"].get(k, "")))
    ign |= {"first", "vocal", "note", "cut", "time", "page", "one", "strum", "instrumental",
            "interlude", "same", "as", "kazoo", "recording", "key", "matches", "based", "on", "capo", "fret", "to", "match", "in"}
    for w in list(lost):
        if w in ign or len(w) < 2 or w.isdigit():
            del lost[w]
    return missing, added, lost

def main(argv):
    import importlib.util, sys, os
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(argv) == 3:                       # input + output only: automatic clean-up
        infile, specfile, outfile = argv[1], None, argv[2]
    elif len(argv) == 4:
        infile, specfile, outfile = argv[1], argv[2], argv[3]
    else:
        print("usage: python songfix.py INPUT.txt [SPEC.py] OUTPUT.txt"); return 1
    specs = {}
    if specfile:
        if not os.path.exists(specfile):
            print("Spec file not found: %s" % specfile); return 1
        spec_mod = importlib.util.spec_from_file_location("spec", specfile)
        m = importlib.util.module_from_spec(spec_mod); spec_mod.loader.exec_module(m)
        if hasattr(m, "SPEC"):
            specs = m.SPEC
        else:
            print("Note: %s has no line  SPEC = {}  -- continuing without section tags.\n" % specfile)
    argv = [argv[0], infile, None, outfile]
    songs = [auto_clean(s) for s in parse_batch(argv[1])]
    chunks, problems = [], 0
    for s in songs:
        built = build(s, specs.get(s["id"], {}))
        missing, added, lost = verify(s, built)
        flag = "OK " if not missing else "BAD"
        if missing: problems += 1
        extra = []
        if added: extra.append("chords added: " + ", ".join("%s x%d" % kv for kv in sorted(added.items())))
        if missing: extra.append("CHORDS MISSING: " + str(dict(missing)))
        if lost: extra.append("words only in original: " + " ".join(list(lost.elements())[:8]))
        if s["id"] not in specs: extra.append("NO SECTION SPEC for this song")
        print("%s %5d %-40s %s" % (flag, s["id"], s["title_hdr"][:40], " | ".join(extra)))
        chunks.append(built)
    open(outfile, "w", encoding="utf-8").write("\n".join(chunks))
    print("\nWrote %s (%d songs, %d with problems)" % (outfile, len(songs), problems))
    return 1 if problems else 0

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
