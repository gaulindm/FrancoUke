import os
import json

# List of instruments to process
INSTRUMENTS = [
    "guitar",
    "guitalele",
    "mandolin",
    "banjo",
    "baritoneUke",
]

STATIC_JS_DIR = os.path.join(os.path.dirname(__file__), "../static/js")

def compute_base_fret(positions):
    """Determine base fret (offset only if lowest fret > 3)."""
    if any(f == 0 for f in positions):
        return 1
    fretted = [f for f in positions if isinstance(f, int) and f > 0]
    if not fretted:
        return 1
    min_fret = min(fretted)
    return min_fret if min_fret > 3 else 1

def detect_barre(positions):
    """Detect barre (adjacent strings with the same fret)."""
    i = 0
    while i < len(positions):
        fret = positions[i]
        if fret > 0:
            start = i
            while i + 1 < len(positions) and positions[i + 1] == fret:
                i += 1
            if i > start:
                return {
                    "fromString": start + 1,
                    "toString": i + 1,
                    "fret": fret
                }
        i += 1
    return None

def migrate_variations(variations):
    """Convert old variations to modern structure."""
    migrated = []
    for var in variations:
        if isinstance(var, dict):
            # Already modern
            migrated.append(var)
        else:
            base_fret = compute_base_fret(var)
            barre = detect_barre(var)
            migrated.append({
                "positions": var,
                "baseFret": base_fret,
                **({"barre": barre} if barre else {})
            })
    return migrated

def migrate_instrument(instrument):
    input_path = os.path.join(STATIC_JS_DIR, f"{instrument}_chords.json")
    backend_path = os.path.join(STATIC_JS_DIR, f"{instrument}_chords_backend.json")
    frontend_path = os.path.join(STATIC_JS_DIR, f"{instrument}_chords_frontend.json")

    if not os.path.exists(input_path):
        print(f"❌ {input_path} not found.")
        return

    print(f"Processing {instrument} chords...")

    with open(input_path, "r", encoding="utf-8") as infile:
        chord_data = json.load(infile)

    migrated_data = [
        {"name": chord["name"], "variations": migrate_variations(chord["variations"])}
        for chord in chord_data
    ]

    # Backend JSON (array)
    with open(backend_path, "w", encoding="utf-8") as backend_file:
        json.dump(migrated_data, backend_file, indent=2)

    # Frontend JSONL
    with open(frontend_path, "w", encoding="utf-8") as frontend_file:
        for chord in migrated_data:
            frontend_file.write(json.dumps(chord, separators=(",", ":")) + "\n")

    print(f"✅ Migrated {instrument} → {backend_path} & {frontend_path}")

def main():
    for instrument in INSTRUMENTS:
        migrate_instrument(instrument)

if __name__ == "__main__":
    main()
