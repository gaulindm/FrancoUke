/* chord_diagrams.js */
function adaptPositionsForInstrument(positions, instrument) {
  switch (instrument) {
    case "baritone_ukulele":
      // 4-string tuning: D-G-B-E (like top 4 of guitar)
      return positions.slice(-4);
    case "guitar":
      return padTo6Strings(positions);
    case "guitalele":
      return padTo6Strings(positions); // but transposed
    case "mandolin":
      return positions.slice(-4); // 4 double strings
    case "banjo":
      return positions.slice(-5); // standard 5-string
    default:
      return positions; // ukulele (default 4 strings)
  }
}

/**
 * Normalize and clean chord names so they match the chord dictionary keys.
 * Handles things like:
 *   - Em/// → Em
 *   - D/F# → D
 *   - Cmaj7 → CM7
 *   - D#dim → Ebdim (enharmonic normalization)
 */
function cleanChordName(chord) {
  if (!chord) return "";

  // Trim brackets if passed in like "[Em///]"
  chord = chord.replace(/^\[|\]$/g, "").trim();

  // 🧹 Remove trailing strumming slashes (Em/// → Em)
  chord = chord.replace(/\/+$/g, "");

  // 🧹 Remove alternate bass (D/F# → D)
  chord = chord.replace(/\/[A-G][#b]?$/i, "");

  // 🧠 Normalize maj variants (Cmaj7, CΔ7 → CM7)
  chord = chord.replace(/maj/i, "M").replace(/Δ/g, "M");

  // 🎵 Normalize enharmonic equivalents
  const ENHARMONIC_EQUIVALENTS = {
    'Cb': 'B',
    'Fb': 'E',
    'E#': 'F',
    'B#': 'C',
    'Db': 'C#',
    'Eb': 'D#',
    'Gb': 'F#',
    'Ab': 'G#',
    'Bb': 'A#',
  };

  // Break into root + suffix
  const match = chord.match(/^([A-G][b#]?)(.*)$/);
  if (match) {
    const [, root, suffix] = match;
    const normalizedRoot = ENHARMONIC_EQUIVALENTS[root] || root;
    chord = normalizedRoot + suffix;
  }

  return chord.toUpperCase();
}




function padTo6Strings(positions) {
  if (positions.length === 6) return positions;
  if (positions.length < 6) {
    return new Array(6 - positions.length).fill(-1).concat(positions);
  }
  return positions.slice(-6); // trim if too many
}

function drawChordDiagram(container, chord, options = {}) {
  if (!container) {
    console.error("❌ drawChordDiagram called with no container");
    return;
  }

  const scale = options.scale || 1;

  const prefs = window.userPreferences || {};
  console.log("📦 Preferences in JS:", prefs);

  // 🎸 Extract positions + baseFret from chord (support both schemas)
  let positions = [];
  let baseFret = 1;

  if (chord.variations && chord.variations.length > 0) {
    // ✅ JSON schema with variations
    positions = chord.variations[0].positions || [];
    baseFret = chord.variations[0].baseFret || 1;
  } else {
    // ✅ Old style fallback
    positions = chord.positions || [];
    baseFret = chord.baseFret || 1;
  }

  console.groupCollapsed(`🎸 Drawing chord: ${chord.name || "Unnamed"}`);
  console.log("Raw positions:", positions, "baseFret:", baseFret);

  // 🔄 Left-handed adjustment
  if (prefs.isLefty) {
    positions = [...positions].reverse();
    console.log("%cApplied left-handed flip", "color: orange", positions);
  }

  // 🎸 Instrument-specific tuning
  const instrument = prefs.instrument || "ukulele";
  positions = adaptPositionsForInstrument(positions, instrument);

  console.log("%cInstrument adaptation:", "color: purple", instrument, positions);

  if (positions.length === 0) {
    console.warn("⚠️ No positions in chord:", chord.name);
    console.groupEnd();
    return;
  }

  const barre = chord.barre || detectBarre(positions);
  const name = chord.name || "Chord";

  console.log("%cFinal positions:", "color: green", positions);
  console.log("%cBase fret:", "color: green", baseFret);
  console.log("%cBarre:", "color: green", barre);
  console.groupEnd();

  // --- SVG SETUP (all constants scaled; scale=1 matches original exactly) ---
  const stringCount = positions.length;
  const fretCount = 5;
  const stringSpacing = 20 * scale;
  const fretSpacing = 20 * scale;
  const radius = Math.max(2, 5 * scale);
  const leftMargin = 20 * scale;
  const topMargin = 40 * scale;
  const bottomPad = 20 * scale;
  const titleFontSize = Math.max(8, 28 * scale);
  const fretLabelFontSize = Math.max(8, 30 * scale);
  const openMuteFontSize = Math.max(6, 12 * scale);
  const strokeWidthThick = Math.max(1, 4 * scale);
  const strokeWidthThin = Math.max(1, 2 * scale);

  const width = (stringCount - 1) * stringSpacing + 2 * leftMargin;
  const height = fretCount * fretSpacing + topMargin + bottomPad;

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);

  // --- Title (Chord Name) ---
  const title = document.createElementNS("http://www.w3.org/2000/svg", "text");
  title.setAttribute("x", width / 2);
  title.setAttribute("y", topMargin * 0.5);
  title.setAttribute("text-anchor", "middle");
  title.setAttribute("font-family", "Helvetica");
  title.setAttribute("font-size", titleFontSize);
  title.setAttribute("font-weight", "bold");
  title.setAttribute("fill", "white");
  title.textContent = name;
  svg.appendChild(title);

  // --- Strings ---
  for (let i = 0; i < stringCount; i++) {
    const x = leftMargin + i * stringSpacing;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", x);
    line.setAttribute("y1", topMargin);
    line.setAttribute("x2", x);
    line.setAttribute("y2", topMargin + fretCount * fretSpacing);
    line.setAttribute("stroke", "white");
    line.setAttribute("stroke-width", strokeWidthThin);
    svg.appendChild(line);
  }

  // --- Frets ---
  for (let j = 0; j <= fretCount; j++) {
    const y = topMargin + j * fretSpacing;
    const fretLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
    fretLine.setAttribute("x1", leftMargin);
    fretLine.setAttribute("y1", y);
    fretLine.setAttribute("x2", leftMargin + (stringCount - 1) * stringSpacing);
    fretLine.setAttribute("y2", y);
    fretLine.setAttribute("stroke", "white");
    fretLine.setAttribute("stroke-width", j === 0 && baseFret === 1 ? strokeWidthThick : strokeWidthThin);
    svg.appendChild(fretLine);
  }

  // --- Fret number label (offset) ---
  if (baseFret > 1) {
    const fretLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
    fretLabel.setAttribute("x", -1 * scale);
    fretLabel.setAttribute("y", topMargin * 1.375);
    fretLabel.setAttribute("font-family", "Helvetica");
    fretLabel.setAttribute("font-size", fretLabelFontSize);
    fretLabel.setAttribute("fill", "white");
    fretLabel.textContent = `${baseFret}`;
    svg.appendChild(fretLabel);
  }

  // --- Barre ---
  if (barre) {
    const adjFret = barre.fret - (baseFret - 1);
    if (adjFret >= 1 && adjFret <= fretCount) {
      const y = topMargin + (adjFret - 0.5) * fretSpacing;
      const x1 = leftMargin + (barre.fromString - 1) * stringSpacing;
      const x2 = leftMargin + (barre.toString - 1) * stringSpacing;
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", x1 - radius);
      rect.setAttribute("y", y - radius);
      rect.setAttribute("width", x2 - x1 + 2 * radius);
      rect.setAttribute("height", 2 * radius);
      rect.setAttribute("rx", 4 * scale);
      rect.setAttribute("fill", "white");
      svg.appendChild(rect);
    }
  }

  // --- Dots / Open / Muted ---
  positions.forEach((fret, i) => {
    const x = leftMargin + i * stringSpacing;

    if (fret > 0) {
      const adjFret = fret - (baseFret - 1);
      const y = topMargin + (adjFret - 0.5) * fretSpacing;
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", x);
      circle.setAttribute("cy", y);
      circle.setAttribute("r", radius);
      circle.setAttribute("fill", "white");
      svg.appendChild(circle);
    } else if (instrument === "guitar") {
      // ✅ Only guitar shows open/muted markers
      if (fret === 0) {
        const o = document.createElementNS("http://www.w3.org/2000/svg", "text");
        o.setAttribute("x", x);
        o.setAttribute("y", topMargin * 0.75);
        o.setAttribute("text-anchor", "middle");
        o.setAttribute("font-size", openMuteFontSize);
        o.setAttribute("fill", "white");
        o.textContent = "O";
        svg.appendChild(o);
      } else if (fret === -1) {
        const xMark = document.createElementNS("http://www.w3.org/2000/svg", "text");
        xMark.setAttribute("x", x);
        xMark.setAttribute("y", topMargin * 0.75);
        xMark.setAttribute("text-anchor", "middle");
        xMark.setAttribute("font-size", openMuteFontSize);
        xMark.setAttribute("fill", "white");
        xMark.textContent = "X";
        svg.appendChild(xMark);
      }
    }
  });

// --- create outer wrapper ---
const outerWrapper = document.createElement("div");
outerWrapper.classList.add("chord-outer-wrapper");

// --- create inner wrapper with SVG ---
const innerWrapper = document.createElement("div");
innerWrapper.classList.add("chord-wrapper");
innerWrapper.appendChild(svg);

// --- append inner to outer, then outer to container ---
outerWrapper.appendChild(innerWrapper);
container.appendChild(outerWrapper);

}



// -------------------------
// Helper functions
// -------------------------
function computeBaseFret(positions) {
  if (positions.some(f => f === 0)) return 1;
  const fretted = positions.filter(f => f > 0);
  if (fretted.length === 0) return 1;
  const minFret = Math.min(...fretted);
  return minFret > 3 ? minFret : 1;
}

function detectBarre(positions) {
  for (let i = 0; i < positions.length; i++) {
    const fret = positions[i];
    if (fret > 0) {
      let j = i;
      while (j + 1 < positions.length && positions[j + 1] === fret) {
        j++;
      }
      if (j > i) {
        return { fromString: i + 1, toString: j + 1, fret };
      }
    }
  }
  return null;
}