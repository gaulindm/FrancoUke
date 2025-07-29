import json

def detect_base_fret(positions):
    """Return the base fret for modern chord diagrams.
    Rule: Only apply offset if all fretted notes are > 3 and no open strings."""
    if any(f == 0 for f in positions):  # open string present
        return 1

    fretted = [f for f in positions if isinstance(f, int) and f > 0]
    if not fretted:
        return 1

    min_fret = min(fretted)
    return min_fret if min_fret > 3 else 1


def detect_barre(positions):
    """Detect a simple barre (two or more adjacent strings with the same fret)."""
    barre_segments = []
    i = 0
    while i < len(positions):
        fret = positions[i]
        if fret > 0:
            start = i
            while i + 1 < len(positions) and positions[i + 1] == fret:
                i += 1
            if i > start:  # Found at least 2 adjacent strings with same fret
                barre_segments.append((start + 1, i + 1, fret))
        i += 1

    # Return only the first barre segment (for simplicity)
    if barre_segments:
        from_string, to_string, fret = barre_segments[0]
        return {
            "fromString": from_string,
            "toString": to_string,
            "fret": fret
        }
    return None

def migrate_chord_variations(variations):
    """Convert old-style chord variations to modern object format."""
    migrated = []
    for var in variations:
        if isinstance(var, dict):  # Already in modern format
            migrated.append(var)
            continue

        base_fret = detect_base_fret(var)
        barre = detect_barre(var)

        new_var = {
            "positions": var,
            "baseFret": base_fret
        }
        if barre:
            new_var["barre"] = barre
        migrated.append(new_var)
    return migrated

def migrate_file(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            chord_data = json.load(infile)
        print(f"📥 Loaded {len(chord_data)} chords from {input_path}")
    except Exception as e:
        print(f"❌ Failed to load input file: {e}")
        return

    migrated_data = []
    for chord in chord_data:
        migrated_data.append({
            "name": chord["name"],
            "variations": migrate_chord_variations(chord["variations"])
        })

    try:
        with open(output_path, "w", encoding="utf-8") as outfile:
            for chord in migrated_data:
                json_line = json.dumps(chord, separators=(",", ":"), ensure_ascii=False)
                outfile.write(json_line + "\n")
        print(f"✅ Migrated data written to {output_path}")
    except Exception as e:
        print(f"❌ Failed to write output file: {e}")

# Example usage
if __name__ == "__main__":
    migrate_file(
        "../static/js/ukulele_chords.json",
        "../static/js/ukulele_chords_migrated.json"
    )
