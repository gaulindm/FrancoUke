# songbook/views/chord_views.py
import os
import json
import re
from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from songbook.utils.chords.loader import load_chords
from songbook.utils.chord_diagram_svg import render_chord_svg


# ---------------------------------------------------------------------
# Constants (moved from main views.py)
# ---------------------------------------------------------------------

ROOTS = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

CHORD_TABS = {
    "triads": ["", "m", "aug", "dim"],
    "sevenths": ["7", "m7", "M7", "aug7", "m7b5", "mMaj7"],
    "suspended": ["sus2", "sus4", "7sus2", "7sus4"],
    "extended": ["9", "m9", "M9", "11", "m11", "13", "m13"],
    "added": ["5", "6", "m6", "add9", "madd9"],
}

ALLOWED_INSTRUMENTS = {
    "ukulele", "guitar", "guitalele", "banjo", "mandolin", "baritoneUke",
}

INSTRUMENTS = [
    "ukulele", "guitalele", "guitar", "banjo", "mandolin", "baritone_ukulele",
]

# ---------------------------------------------------------------------
# Chord JSON endpoints
# ---------------------------------------------------------------------

def serve_chords_json(request, instrument):
    if instrument not in ALLOWED_INSTRUMENTS:
        raise Http404("Instrument not supported")

    file_path = os.path.join(
        settings.BASE_DIR, "songbook", "chords", f"{instrument}.json"
    )
    if not os.path.exists(file_path):
        raise Http404("Chord file not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return JsonResponse(json.load(f), safe=False)


def get_chord_definition(request, chord_name):
    chords = load_chords()
    for chord in chords:
        if chord.get("name", "").lower() == chord_name.lower():
            return JsonResponse({"success": True, "chord": chord})
    return JsonResponse(
        {"success": False, "error": f"Chord '{chord_name}' not found."}
    )

# ---------------------------------------------------------------------
# Chord Dictionary Page
# ---------------------------------------------------------------------

@require_GET
def chord_dictionary(request):
    instrument = request.GET.get("instrument", "ukulele")
    site_name = request.resolver_match.namespace
    lefty = request.GET.get("lefty") in ["1", "true", "on"]
    show_alt = request.GET.get("show_alt") in ["1", "true", "on"]

    tab = request.GET.get("tab", "triads")
    allowed_types = CHORD_TABS.get(tab, CHORD_TABS["triads"])

    chords = load_chords(instrument)

    # DEBUG
    print("=== DEBUG chord_dictionary ===")
    print("Instrument:", instrument)
    print("Loaded chords:", len(chords))
    if chords:
        print("First chord:", chords[0])
    else:
        print("NO chords loaded!")



    grouped = {root: {} for root in ROOTS}

    for chord in chords:
        name = chord.get("name")
        variations_raw = chord.get("variations", [])

        if not name or not variations_raw:
            continue

        match = re.match(r"([A-G][b#]?)(.*)", name)
        if not match:
            continue

        root = match.group(1)
        ctype = match.group(2) or ""

        if ctype not in allowed_types:
            continue

        variations = []
        for v in variations_raw:
            main_svg = render_chord_svg(name, v, instrument, is_lefty=lefty, scale=1.0)
            small_svg = render_chord_svg(name, v, instrument, is_lefty=lefty, scale=0.5)

            variations.append({
                "name": name,
                "main_svg": main_svg,
                "small_svg": small_svg,
            })

        grouped[root][ctype] = variations

    # Build table rows
    rows = []
    for ctype in allowed_types:
        row = {"type": ctype, "cells": []}
        for root in ROOTS:
            variations = grouped.get(root, {}).get(ctype)
            if not variations:
                row["cells"].append(None)
                continue

            main = variations[0]
            smalls = [v["small_svg"] for v in variations[1:3]] if show_alt else []

            row["cells"].append({
                "name": main["name"],
                "main_svg": main["main_svg"],
                "small_svgs": smalls,
            })

        rows.append(row)

    context = {
        "site_name": site_name,
        "instrument": instrument,
        "lefty": lefty,
        "show_alt": show_alt,
        "tab": tab,
        "roots": ROOTS,
        "rows": rows,
        "instruments": INSTRUMENTS,
        "CHORD_TABS": CHORD_TABS,
    }

    return render(request, "chords/chord_dictionary.html", context)
