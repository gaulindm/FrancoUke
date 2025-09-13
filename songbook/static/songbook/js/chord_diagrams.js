function drawChordDiagram(container, chord) {
    const { name, variation } = chord;
    const positions = variation.positions || [];
    const baseFret = variation.baseFret || computeBaseFret(positions);
    const barre = variation.barre || detectBarre(positions);
  
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
  
    // --- Title (Chord Name) ---
    const title = document.createElementNS("http://www.w3.org/2000/svg", "text");
    title.setAttribute("x", width / 2);
    title.setAttribute("y", 20);
    title.setAttribute("text-anchor", "middle");
    title.setAttribute("font-family", "Helvetica");
    title.setAttribute("font-size", "18");
    title.setAttribute("font-weight", "bold");
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
      line.setAttribute("stroke", "black");
      line.setAttribute("stroke-width", "2");
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
      fretLine.setAttribute("stroke", "black");
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
        rect.setAttribute("fill", "black");
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
        circle.setAttribute("fill", "black");
        svg.appendChild(circle);
      } else if (fret === 0) {
        const o = document.createElementNS("http://www.w3.org/2000/svg", "text");
        o.setAttribute("x", x);
        o.setAttribute("y", 30);
        o.setAttribute("text-anchor", "middle");
        o.setAttribute("font-size", "12");
        o.textContent = "O";
        svg.appendChild(o);
      } else if (fret === -1) {
        const xMark = document.createElementNS("http://www.w3.org/2000/svg", "text");
        xMark.setAttribute("x", x);
        xMark.setAttribute("y", 30);
        xMark.setAttribute("text-anchor", "middle");
        xMark.setAttribute("font-size", "12");
        xMark.textContent = "X";
        svg.appendChild(xMark);
      }
    });
  
    container.appendChild(svg);
  }

  
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

  
  // Example chord variation (like your JSON files)
const chord = {
    name: "C",
    variation: {
      positions: [0, 0, 0, 3], // ukulele C chord
      baseFret: 1,
      barre: null
    }
  };
  
  const container = document.getElementById("chord-diagrams");
  drawChordDiagram(container, chord);
  