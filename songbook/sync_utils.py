"""
songbook/sync_utils.py  --  helpers for copying already-formatted ChordPro from the
local copy of the songbook to the production copy, matching songs by TITLE
(ids differ between the two databases).
"""
import difflib
import hashlib
import re
import unicodedata

CHORD = (r"\*?[A-G][#b]?(?:maj|min|dim|aug|sus|add|m|M|o|\+)?\d*(?:[b#+]\d+)*"
         r"(?:sus\d?|add\d+)?(?:/(?:[A-G][#b]?|\d))?\*?")


def sha1_text(text):
    return hashlib.sha1((text or "").replace("\r\n", "\n").strip().encode("utf-8")).hexdigest()


# ---- titles -----------------------------------------------------------------
def _basic(t):
    t = unicodedata.normalize("NFKD", t or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().replace("\u2019", "'").replace("`", "'")
    t = re.sub(r"[^a-z0-9' ]+", " ", t)          # hyphens, commas, punctuation -> space
    t = t.replace("'", "")
    return re.sub(r"\s+", " ", t).strip()


def norm_title(t):
    """'Boxer, The' / 'The Boxer' / 'The-Boxer' all become 'boxer'."""
    b = _basic(t)
    m = re.match(r"^(.*) (the|a|an)$", b)
    if m:
        b = m.group(2) + " " + m.group(1)
    return re.sub(r"^(the|a|an) ", "", b)


def title_keys(title):
    """Keys to try, strictest first."""
    n = norm_title(title)
    keys = [n, n.replace(" ", "")]
    no_paren = norm_title(re.sub(r"\([^)]*\)", " ", title or ""))
    for k in (no_paren, no_paren.replace(" ", "")):
        if k and k not in keys:
            keys.append(k)
    return [k for k in keys if k]


# ---- comparing song texts -------------------------------------------------------
def chord_set(text):
    out = set()
    for tok in re.findall(r"\[([^\]]+)\]", text or ""):
        for part in re.split(r"\s*-\s*", tok.strip()):
            part = part.rstrip("/")
            if re.fullmatch(CHORD, part):
                out.add(part)
    return out


_JUNK = re.compile(r"first vocal note\s*=\s*\S+|\b\d+/\d+\b|\bcut time\b|\bcount in\s*=\s*\S+|"
                   r"^\s*(?:interlude|instrumental)[^:\n]*:", re.I | re.M)


def lyric_words(text):
    t = re.sub(r"\{[^}]*\}", " ", text or "")
    t = re.sub(r"\[[^\]]*\]", " ", t)
    t = _JUNK.sub(" ", t)                      # PDF header junk is not part of the lyrics
    return set(re.sub(r"[^a-z0-9 ]", " ", t.lower().replace("\u2019", "'")).split())


def similarity(a, b):
    wa, wb = lyric_words(a), lyric_words(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


# ---- matching ---------------------------------------------------------------------
def match_songs(prod, local, allow_unformatted=True, min_sim=0.75, allow_chord_diff=False):
    """
    prod  : list of dicts  id, title, origin, chordpro, sha1
    local : list of dicts  id, title, origin, chordpro, formatted, revised_on
    Returns one result dict per production song with a 'status':
      ok, identical, no_local_match, local_not_fixed, low_similarity, ambiguous, chords_differ
    Only 'ok' results carry the local text to copy.
    allow_unformatted=True (default): a local song counts whether or not it has formatting rows;
    with False only local songs that are formatted are used ('local_not_fixed' otherwise).
    """
    index = {}
    for i, s in enumerate(local):
        for k in title_keys(s["title"]):
            index.setdefault(k, []).append(i)
    index_keys = list(index)

    results = []
    for p in prod:
        res = {"prod_id": p["id"], "prod_title": p["title"], "prod_sha1": p.get("sha1") or sha1_text(p["chordpro"]),
               "status": "", "local_id": None, "local_title": "", "similarity": None, "note": ""}
        idxs = []
        for k in title_keys(p["title"]):
            if k in index:
                idxs = index[k]
                break
        cands = [local[i] for i in dict.fromkeys(idxs)]
        if not cands:
            res["status"] = "no_local_match"
            close = difflib.get_close_matches(norm_title(p["title"]), index_keys, n=1, cutoff=0.85)
            if close:
                c = local[index[close[0]][0]]
                res["note"] = "closest local title: %r (#%s)" % (c["title"], c["id"])
            results.append(res); continue
        usable = [c for c in cands if c["formatted"] or allow_unformatted]
        if not usable:
            res["status"] = "local_not_fixed"
            res["local_id"] = cands[0]["id"]; res["local_title"] = cands[0]["title"]
            results.append(res); continue
        scored = sorted(((similarity(p["chordpro"], c["chordpro"]), c) for c in usable),
                        key=lambda x: -x[0])
        best_sim, best = scored[0]
        close = [c for s_, c in scored if s_ >= best_sim - 0.02]
        distinct = {sha1_text(c["chordpro"]) for c in close}
        if len(distinct) > 1:
            same_origin = [c for c in close if p.get("origin") and
                           (c.get("origin") or "").lower() == p["origin"].lower()]
            if len({sha1_text(c["chordpro"]) for c in same_origin}) == 1:
                best = same_origin[0]
            else:
                res["status"] = "ambiguous"
                res["note"] = "local ids " + ", ".join(str(c["id"]) for c in close)
                results.append(res); continue
        res.update(local_id=best["id"], local_title=best["title"], similarity=round(best_sim, 2))
        if best_sim < min_sim:
            res["status"] = "low_similarity"; results.append(res); continue
        if sha1_text(best["chordpro"]) == res["prod_sha1"]:
            res["status"] = "identical"; results.append(res); continue
        cp, cl = chord_set(p["chordpro"]), chord_set(best["chordpro"])
        if cp != cl and not allow_chord_diff:
            res["status"] = "chords_differ"
            res["note"] = "only on production: %s | only local: %s" % (
                " ".join(sorted(cp - cl)) or "-", " ".join(sorted(cl - cp)) or "-")
            results.append(res); continue
        res["status"] = "ok"
        res["chordpro"] = best["chordpro"]
        res["revised_on"] = best.get("revised_on") or ""
        results.append(res)
    return results