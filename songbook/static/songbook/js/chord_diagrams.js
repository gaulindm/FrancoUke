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

function padTo6Strings(positions) {
  if (positions.length === 6) return positions;
  if (positions.length < 6) {
    return new Array(6 - positions.length).fill(-1).concat(positions);
  }
  return positions.slice(-6); // trim if too many
}

function drawChordDiagram(container, chord) {
  if (!container) {
    console.error("❌ drawChordDiagram called with no container");
    return;
  }

  const prefs = window.userPreferences || {};
  console.log("📦 Preferences in JS:", prefs);

  let positions = chord.positions || [];
  console.log("🎸 Drawing chord:", chord.name, "Raw positions:", positions);

  // 🔄 Left-handed adjustment (reverse string order only)
  const isLefty = prefs.isLefty || false;
  if (isLefty) {
    positions = [...positions].reverse();
    console.log("🔁 Applied left-handed flip:", positions);
  }

  // 🎸 Instrument-specific adaptation
  const instrument = prefs.instrument || "ukulele";
  positions = adaptPositionsForInstrument(positions, instrument);
  console.log("Instrument adaptation:", instrument, positions);

  if (positions.length === 0) {
    console.warn("⚠️ No positions in chord:", chord.name);
    return;
  }

  const baseFret = chord.baseFret || computeBaseFret(positions);
  const barre = chord.barre || detectBarre(positions);
  const name = chord.name || "Chord";

  const stringCount = positions.length;
  const fretCount = 5;
  const stringSpacing = 20;
  const fretSpacing = 20;
  const radius = 5;

  const width = (stringCount - 1) * stringSpacing + 40;
  const height = fretCount * fretSpacing + 60;

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);

  // --- Title (Chord Name) stays upright ---
  const title = document.createElementNS("http://www.w3.org/2000/svg", "text");
  title.setAttribute("x", width / 2);
  title.setAttribute("y", 20);
  title.setAttribute("text-anchor", "middle");
  title.setAttribute("font-family", "Helvetica");
  title.setAttribute("font-size", "28");
  title.setAttribute("font-weight", "bold");
  title.setAttribute("fill", "white");
  title.textContent = name;
  svg.appendChild(title);

  // --- Strings ---
  for (let i = 0; i < stringCount; i++) {
    const x = 20 + i * stringSpacing;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", x);
    line.setAttribute("y1", 40);
    line.setAttribute("x2", x);
    line.setAttribute("y2", 40 + fretCount * fretSpacing);
    line.setAttribute("stroke", "white");
    line.setAttribute("stroke-width", 2);
    svg.appendChild(line);
  }

  // --- Frets ---
  for (let j = 0; j <= fretCount; j++) {
    const y = 40 + j * fretSpacing;
    const fretLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
    fretLine.setAttribute("x1", 20);
    fretLine.setAttribute("y1", y);
    fretLine.setAttribute("x2", 20 + (stringCount - 1) * stringSpacing);
    fretLine.setAttribute("y2", y);
    fretLine.setAttribute("stroke", "white");
    fretLine.setAttribute("stroke-width", j === 0 && baseFret === 1 ? 4 : 2);
    svg.appendChild(fretLine);
  }

  // --- Barre ---
  if (barre) {
    const adjFret = barre.fret - (baseFret - 1);
    if (adjFret >= 1 && adjFret <= fretCount) {
      const y = 40 + (adjFret - 0.5) * fretSpacing;
      const x1 = 20 + (barre.fromString - 1) * stringSpacing;
      const x2 = 20 + (barre.toString - 1) * stringSpacing;
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", x1 - radius);
      rect.setAttribute("y", y - radius);
      rect.setAttribute("width", x2 - x1 + 2 * radius);
      rect.setAttribute("height", 2 * radius);
      rect.setAttribute("rx", 4);
      rect.setAttribute("fill", "white");
      svg.appendChild(rect);
    }
  }

  // --- Dots / Open / Muted ---
  positions.forEach((fret, i) => {
    const x = 20 + i * stringSpacing;
    if (fret > 0) {
      const adjFret = fret - (baseFret - 1);
      const y = 40 + (adjFret - 0.5) * fretSpacing;
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", x);
      circle.setAttribute("cy", y);
      circle.setAttribute("r", radius);
      circle.setAttribute("fill", "white");
      svg.appendChild(circle);
    } else if (fret === 0) {
      const o = document.createElementNS("http://www.w3.org/2000/svg", "text");
      o.setAttribute("x", x);
      o.setAttribute("y", 30);
      o.setAttribute("text-anchor", "middle");
      o.setAttribute("font-size", 12);
      o.setAttribute("fill", "white");
      o.textContent = "O";
      svg.appendChild(o);
    } else if (fret === -1) {
      const xMark = document.createElementNS("http://www.w3.org/2000/svg", "text");
      xMark.setAttribute("x", x);
      xMark.setAttribute("y", 30);
      xMark.setAttribute("text-anchor", "middle");
      xMark.setAttribute("font-size", 12);
      xMark.setAttribute("fill", "white");
      xMark.textContent = "X";
      svg.appendChild(xMark);
    }
  });

  const wrapper = document.createElement("div");
  wrapper.style.display = "inline-block";
  wrapper.style.transform = "scale(1.0)";
  wrapper.style.transformOrigin = "top left";
  wrapper.style.margin = "2px";
  wrapper.appendChild(svg);

  container.appendChild(wrapper);
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


