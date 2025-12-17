// cube.js - Fonctions pour visualiser l'étape de la marguerite

// Couleurs standard du cube
const COLORS = {
  white: '#FFFFFF',
  yellow: '#FFFF00',
  green: '#00FF00',
  blue: '#0000FF',
  red: '#FF0000',
  orange: '#FFA500',
  gray: '#CCCCCC',
  highlight: '#FFFF00'
};


// Get color scheme based on front color orientation
// This replaces the repetitive 'rotations' object in every function
function getColorScheme(frontColor = 'green') {
  const rotations = {
    'green': { F: COLORS.green, R: COLORS.red, B: COLORS.blue, L: COLORS.orange },
    'red': { F: COLORS.red, R: COLORS.blue, B: COLORS.orange, L: COLORS.green },
    'blue': { F: COLORS.blue, R: COLORS.orange, B: COLORS.green, L: COLORS.red },
    'orange': { F: COLORS.orange, R: COLORS.green, B: COLORS.red, L: COLORS.blue }
  };
  return rotations[frontColor] || rotations['green'];
}

// Fonction utilitaire pour colorer une sticker avec un préfixe pour l'ID unique
function colorSticker(id, color, prefix = '') {
  const fullId = prefix ? `${prefix}-${id}` : id;
  const sticker = document.getElementById(fullId);
  if (sticker) {
    sticker.style.fill = color;
    sticker.style.stroke = '#333';
    sticker.style.strokeWidth = '1.5';
  }
}

// ============================================
// BASE FUNCTIONS - Building blocks for all states
// ============================================

// Standard color scheme (default orientation)
// Top = Yellow, Bottom = White, Front = Green
const STANDARD_CENTERS = {
  U: 'yellow',   // Top (always yellow)
  D: 'white',    // Down (always white)
  F: 'green',    // Front
  R: 'orange',      // Right
  B: 'blue',     // Back
  L: 'red'    // Left
};

// Set centers based on which color is front
// Yellow always stays on top, white always on bottom
// The 4 side colors rotate based on frontColor
function setCenters(prefix = '', frontColor = 'green') {
  // Always the same
  colorSticker('sticker-U-1-1', COLORS.yellow, prefix);   // Top = Yellow
  colorSticker('sticker-D-1-1', COLORS.white, prefix);    // Down = White
  
  // Side colors rotate based on front
  const rotations = {
    'green': {
      F: COLORS.green,
      R: COLORS.orange,
      B: COLORS.blue,
      L: COLORS.red
    },
    'red': {
      F: COLORS.red,
      R: COLORS.green,
      B: COLORS.orange,
      L: COLORS.blue
    },
    'blue': {
      F: COLORS.blue,
      R: COLORS.red,
      B: COLORS.green,
      L: COLORS.orange
    },
    'orange': {
      F: COLORS.orange,
      R: COLORS.blue,
      B: COLORS.red,
      L: COLORS.green
    }
  };
  
  const scheme = rotations[frontColor] || rotations['green'];
  colorSticker('sticker-F-1-1', scheme.F, prefix);
  colorSticker('sticker-R-1-1', scheme.R, prefix);
  colorSticker('sticker-B-1-1', scheme.B, prefix);
  colorSticker('sticker-L-1-1', scheme.L, prefix);
}

// ============================================
// LAYER BUILDING FUNCTIONS (Build up from bottom)
// ============================================

// Build white cross on bottom (4 edges)
// This is the base layer for all subsequent steps
function buildWhiteCross(prefix = '', frontColor = 'green') {
  const scheme = getColorScheme(frontColor);
  
  // White cross on bottom (4 white edges forming a +)
  colorSticker('sticker-D-0-1', COLORS.white, prefix);  // Top edge
  colorSticker('sticker-D-1-0', COLORS.white, prefix);  // Left edge
  colorSticker('sticker-D-1-2', COLORS.white, prefix);  // Right edge
  colorSticker('sticker-D-2-1', COLORS.white, prefix);  // Bottom edge
  
  // Matching side colors (the "correct" cross)
  colorSticker('sticker-F-2-1', scheme.F, prefix);
  colorSticker('sticker-R-2-1', scheme.R, prefix);
  colorSticker('sticker-B-2-1', scheme.B, prefix);
  colorSticker('sticker-L-2-1', scheme.L, prefix);
}

// Build white corners on bottom (completes first layer)
// Assumes white cross is already built
function buildWhiteCorners(prefix = '', frontColor = 'green') {
  const scheme = getColorScheme(frontColor);
  
  // 4 white corners on bottom with matching side colors
  // Front-Right corner
  colorSticker('sticker-D-0-2', COLORS.white, prefix);
  colorSticker('sticker-F-2-2', scheme.F, prefix);
  colorSticker('sticker-R-2-0', scheme.R, prefix);
  
  // Back-Right corner
  colorSticker('sticker-D-2-2', COLORS.white, prefix);
  colorSticker('sticker-R-2-2', scheme.R, prefix);
  colorSticker('sticker-B-2-0', scheme.B, prefix);
  
  // Back-Left corner
  colorSticker('sticker-D-2-0', COLORS.white, prefix);
  colorSticker('sticker-B-2-2', scheme.B, prefix);
  colorSticker('sticker-L-2-0', scheme.L, prefix);
  
  // Front-Left corner
  colorSticker('sticker-D-0-0', COLORS.white, prefix);
  colorSticker('sticker-L-2-2', scheme.L, prefix);
  colorSticker('sticker-F-2-0', scheme.F, prefix);
}

// Build complete first layer (white cross + white corners)
function buildFirstLayer(prefix = '', frontColor = 'green') {
  buildWhiteCross(prefix, frontColor);
  buildWhiteCorners(prefix, frontColor);
}

// Build middle layer (second layer edges)
// Assumes first layer is already built
function buildMiddleLayer(prefix = '', frontColor = 'green') {
  const scheme = getColorScheme(frontColor);
  
  // Front-Right edge
  colorSticker('sticker-F-1-2', scheme.F, prefix);
  colorSticker('sticker-R-1-0', scheme.R, prefix);
  
  // Back-Right edge
  colorSticker('sticker-R-1-2', scheme.R, prefix);
  colorSticker('sticker-B-1-0', scheme.B, prefix);
  
  // Back-Left edge
  colorSticker('sticker-B-1-2', scheme.B, prefix);
  colorSticker('sticker-L-1-0', scheme.L, prefix);
  
  // Front-Left edge
  colorSticker('sticker-L-1-2', scheme.L, prefix);
  colorSticker('sticker-F-1-0', scheme.F, prefix);
}

// Build first two layers (F2L complete)
function buildFirstTwoLayers(prefix = '', frontColor = 'green') {
  buildFirstLayer(prefix, frontColor);
  buildMiddleLayer(prefix, frontColor);
}

// Reset entire cube to gray
function resetCubeGray(prefix = '') {
  const faces = ['R', 'F', 'U', 'L', 'D', 'B'];
  faces.forEach(face => {
    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < 3; col++) {
        colorSticker(`sticker-${face}-${row}-${col}`, COLORS.gray, prefix);
      }
    }
  });
}

// Reset cube to gray + colored centers (most common starting point)
function resetCubeWithCenters(prefix = '', frontColor = 'green') {
  resetCubeGray(prefix);
  setCenters(prefix, frontColor);
}

// ============================================
// ÉTAT 1 : Marguerite complète (objectif final)
// ============================================
function setDaisy(prefix = '') {
  // Start with gray cube + centers
  resetCubeWithCenters(prefix);
  
  // The 4 white edges around yellow center (the daisy)
  colorSticker('sticker-U-0-1', COLORS.white, prefix);  // Top
  colorSticker('sticker-U-1-0', COLORS.white, prefix);  // Left
  colorSticker('sticker-U-1-2', COLORS.white, prefix);  // Right
  colorSticker('sticker-U-2-1', COLORS.white, prefix);  // Bottom
  
  // Color adjacent edges (other side of same pieces)
  colorSticker('sticker-F-0-1', COLORS.gray, prefix);   // Front edge
  colorSticker('sticker-R-0-1', COLORS.gray, prefix);     // Right edge
  colorSticker('sticker-B-0-1', COLORS.gray, prefix);    // Back edge
  colorSticker('sticker-L-0-1', COLORS.gray, prefix);  // Left edge
}

// ============================================
// ÉTAT 2 : Marguerite avec mise en évidence
// ============================================
function setDaisyHighlighted(prefix = '') {
  setDaisy(prefix);
  
  // Ajouter un effet de surbrillance sur les arêtes blanches
  const whiteEdges = ['sticker-U-0-1', 'sticker-U-1-0', 'sticker-U-1-2', 'sticker-U-2-1'];
  whiteEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 8px red)';
    }
  });
}

// ============================================
// ÉTAT 3 : Progression de la marguerite (0 à 4 pétales)
// ============================================
function setDaisyProgress(numPetals, prefix = '') {
  // Start with gray cube + centers
  resetCubeWithCenters(prefix);
  
  // Add petals progressively
  const petalOrder = [
    'sticker-U-0-1',  // Petal 1 (top)
    'sticker-U-1-2',  // Petal 2 (right)
    'sticker-U-2-1',  // Petal 3 (bottom)
    'sticker-U-1-0'   // Petal 4 (left)
  ];
  
  for (let i = 0; i < numPetals && i < 4; i++) {
    colorSticker(petalOrder[i], COLORS.white, prefix);
  }
  
  // Show where next petal should go (with highlight)
  if (numPetals < 4) {
    const fullId = prefix ? `${prefix}-${petalOrder[numPetals]}` : petalOrder[numPetals];
    const nextPetal = document.getElementById(fullId);
    if (nextPetal) {
      nextPetal.style.fill = '#FFFF99';
      nextPetal.style.stroke = '#FFD700';
      nextPetal.style.strokeWidth = '3';
      nextPetal.style.strokeDasharray = '5,5';
    }
  }
}

// ============================================
// ÉTAT 4 : Cube mélangé avec arêtes blanches dispersées
// ============================================
function setScrambledWithWhiteEdges(prefix = '') {
  // Start with gray cube + centers
  resetCubeWithCenters(prefix);
  
  // Place white EDGES at different locations (scattered)
  // IMPORTANT: Only use edge positions, NOT corners!
  // Edges always have one coordinate = 1
  
  // Edge 1: Front face, middle left (row 1, col 0)
  colorSticker('sticker-F-1-0', COLORS.white, prefix);
  
  // Edge 2: Right face, middle bottom (row 2, col 1)
  colorSticker('sticker-R-2-1', COLORS.white, prefix);
  
  // Edge 3: Down face, middle top (row 0, col 1)
  colorSticker('sticker-D-0-1', COLORS.white, prefix);
  
  // Edge 4: Left face, middle right (row 1, col 2)
  colorSticker('sticker-L-1-2', COLORS.white, prefix);
  
  // Add visual effect to make them stand out
  const whiteEdges = ['sticker-F-1-0', 'sticker-R-2-1', 'sticker-D-0-1', 'sticker-L-1-2'];
  whiteEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px white)';
      sticker.style.strokeWidth = '2.5';
    }
  });
  
}

// ============================================
// FONCTION UTILITAIRE : Cloner le cube avec IDs uniques
// ============================================
function cloneCubeWithUniqueIds(containerId, prefix) {
  const template = document.getElementById("cube-template");
  if (!template) {
    console.error("Template cube-template introuvable");
    return null;
  }
  
  const clone = template.content.cloneNode(true);
  
  // Ajouter un préfixe unique à tous les IDs dans le clone
  const elementsWithIds = clone.querySelectorAll('[id]');
  elementsWithIds.forEach(element => {
    const oldId = element.id;
    element.id = `${prefix}-${oldId}`;
  });
  
  return clone;
}

// ============================================
// FONCTION PRINCIPALE : Insérer un cube coloré
// ============================================
function insertCubeInContainer(containerId, colorFunction, prefix) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container ${containerId} introuvable`);
    return;
  }
  
  const clone = cloneCubeWithUniqueIds(containerId, prefix);
  if (!clone) return;
  
  container.appendChild(clone);
  
  // Appliquer la fonction de coloration avec le préfixe
  if (typeof colorFunction === 'function') {
    colorFunction(prefix);
  }
}

// ============================================
// STEP 1B: WHITE CROSS
// ============================================

// Complete white cross with matching side colors
function setWhiteCross(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildWhiteCross(prefix, frontColor);
}

// White cross highlighted to show the goal
function setWhiteCrossHighlighted(prefix = '', frontColor = 'green') {
  setWhiteCross(prefix, frontColor);
  
  // Add glow effect to white cross
  const crossEdges = ['sticker-D-0-1', 'sticker-D-1-0', 'sticker-D-1-2', 'sticker-D-2-1'];
  crossEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 8px white)';
    }
  });
}

// Show white cross with one corner in position (for teaching)
function setWhiteCrossWithOneCorner(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildWhiteCross(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Add just the front-right corner
  colorSticker('sticker-D-0-2', COLORS.white, prefix);
  colorSticker('sticker-F-2-2', scheme.F, prefix);
  colorSticker('sticker-R-2-0', scheme.R, prefix);
}

// Show corner in top layer ready to be inserted (white facing right)
function setCornerInTopWhiteRight(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildWhiteCross(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Corner with white facing RIGHT
  colorSticker('sticker-R-0-0', COLORS.white, prefix);
  colorSticker('sticker-U-0-2', scheme.F, prefix);
  colorSticker('sticker-F-0-2', scheme.R, prefix);
  
  // Highlight
  const cornerIds = ['sticker-R-0-0', 'sticker-U-0-2', 'sticker-F-0-2'];
  cornerIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// Show corner in top layer (white facing front)
function setCornerInTopWhiteFront(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildWhiteCross(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Corner with white facing FRONT
  colorSticker('sticker-F-0-2', COLORS.white, prefix);
  colorSticker('sticker-U-0-2', scheme.R, prefix);
  colorSticker('sticker-R-0-0', scheme.F, prefix);
  
  // Highlight
  const cornerIds = ['sticker-F-0-2', 'sticker-U-0-2', 'sticker-R-0-0'];
  cornerIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// Show corner in top layer (white facing up)
function setCornerInTopWhiteUp(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildWhiteCross(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Corner with white facing UP
  colorSticker('sticker-U-0-2', COLORS.white, prefix);
  colorSticker('sticker-F-0-2', scheme.F, prefix);
  colorSticker('sticker-R-0-0', scheme.R, prefix);
  
  // Highlight
  const cornerIds = ['sticker-U-0-2', 'sticker-F-0-2', 'sticker-R-0-0'];
  cornerIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}


// Complete first layer (white cross + 4 white corners)
function setWhiteCorners(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
}

// White corners highlighted
function setWhiteCornersHighlighted(prefix = '', frontColor = 'green') {
  setWhiteCorners(prefix, frontColor);
  
  // Add glow to corners
  const cornerStickers = [
    'sticker-D-0-0', 'sticker-D-0-2', 'sticker-D-2-0', 'sticker-D-2-2'
  ];
  cornerStickers.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 8px white)';
    }
  });
}



// Show transition from daisy to white cross
function setDaisyToWhiteCrossTransition(prefix = '', edgeNumber = 0, frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Define which edges have been flipped based on edgeNumber (0-4)
  const petalPositions = [
    { top: 'sticker-U-2-1', bottom: 'sticker-D-0-1', side: 'sticker-F-2-1' },  // Front edge
    { top: 'sticker-U-1-2', bottom: 'sticker-D-1-2', side: 'sticker-R-2-1' },  // Right edge
    { top: 'sticker-U-0-1', bottom: 'sticker-D-2-1', side: 'sticker-B-2-1' },  // Back edge
    { top: 'sticker-U-1-0', bottom: 'sticker-D-1-0', side: 'sticker-L-2-1' }   // Left edge
  ];
  
  const sideColors = [scheme.F, scheme.R, scheme.B, scheme.L];
  
  // Show petals that are still on top
  for (let i = edgeNumber; i < 4; i++) {
    colorSticker(petalPositions[i].top, COLORS.white, prefix);
  }
  
  // Show edges that have been flipped to bottom
  for (let i = 0; i < edgeNumber; i++) {
    colorSticker(petalPositions[i].bottom, COLORS.white, prefix);
    colorSticker(petalPositions[i].side, sideColors[i], prefix);
  }
}

// Incorrect white cross (white cross but colors don't match)
function setWhiteCrossIncorrect(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  
  // White cross on bottom
  colorSticker('sticker-D-0-1', COLORS.white, prefix);
  colorSticker('sticker-D-1-0', COLORS.white, prefix);
  colorSticker('sticker-D-1-2', COLORS.white, prefix);
  colorSticker('sticker-D-2-1', COLORS.white, prefix);
  
  // WRONG side colors (mismatched)
  colorSticker('sticker-F-2-1', COLORS.blue, prefix);
  colorSticker('sticker-R-2-1', COLORS.orange, prefix);
  colorSticker('sticker-B-2-1', COLORS.green, prefix);
  colorSticker('sticker-L-2-1', COLORS.red, prefix);
}

// ============================================
// STEP 3: MIDDLE LAYER (SECOND LAYER EDGES)
// ============================================

// Complete first two layers (F2L)
function setMiddleLayerComplete(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
}

// Middle layer complete with highlighted edges
function setMiddleLayerHighlighted(prefix = '', frontColor = 'green') {
  setMiddleLayerComplete(prefix, frontColor);
  
  // Highlight the 4 middle layer edges
  const middleEdges = [
    'sticker-F-1-2', 'sticker-R-1-0',  // Front-Right edge
    'sticker-R-1-2', 'sticker-B-1-0',  // Back-Right edge
    'sticker-B-1-2', 'sticker-L-1-0',  // Back-Left edge
    'sticker-L-1-2', 'sticker-F-1-0'   // Front-Left edge
  ];
  
  middleEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
      sticker.style.strokeWidth = '2';
    }
  });
}

// Show first layer complete (starting point for middle layer)
function setFirstLayerComplete(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
}

// Show edge in top layer ready for RIGHT algorithm (U R U' R' U' F' U F)
// Edge with target color facing FRONT, no yellow
function setMiddleEdgeTopFacingFront(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Edge at front-top position
  // Front sticker matches front center, top sticker matches right center
  colorSticker('sticker-F-0-1', scheme.F, prefix);  // Front face (matches front center)
  colorSticker('sticker-U-2-1', scheme.R, prefix);  // Top face (goes to right)
  
  // Highlight the edge
  const edgeIds = ['sticker-F-0-1', 'sticker-U-2-1'];
  edgeIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// Show edge in top layer ready for LEFT algorithm (U' L' U L U F U' F')
// Edge with target color facing RIGHT, no yellow
function setMiddleEdgeTopFacingRight(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Edge at right-top position
  // Right sticker matches front center, top sticker matches left center
  colorSticker('sticker-R-0-1', scheme.F, prefix);  // Right face (goes to front)
  colorSticker('sticker-U-1-2', scheme.L, prefix);  // Top face (goes to left)
  
  // Highlight the edge
  const edgeIds = ['sticker-R-0-1', 'sticker-U-1-2'];
  edgeIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// Show edge with yellow on top (wrong - needs to be removed first)
function setMiddleEdgeWithYellow(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Edge with YELLOW facing up (bad case)
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);  // Yellow on top
  colorSticker('sticker-F-0-1', scheme.F, prefix);       // Front color
  
  // Highlight with warning color
  const edgeIds = ['sticker-U-2-1', 'sticker-F-0-1'];
  edgeIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px red)';
    }
  });
}

// Show edge stuck in middle layer (needs extraction)
function setMiddleEdgeStuck(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Edge in wrong position in middle layer (front-right slot)
  colorSticker('sticker-F-1-2', scheme.R, prefix);  // Wrong! Should be front color
  colorSticker('sticker-R-1-0', scheme.B, prefix);  // Wrong! Should be right color
  
  // Highlight the stuck edge
  const edgeIds = ['sticker-F-1-2', 'sticker-R-1-0'];
  edgeIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.strokeWidth = '3';
      sticker.style.filter = 'drop-shadow(0 0 6px orange)';
    }
  });
}

// Show one middle edge inserted (for teaching progression)
function setMiddleLayerOneEdge(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstLayer(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Just the front-right middle edge
  colorSticker('sticker-F-1-2', scheme.F, prefix);
  colorSticker('sticker-R-1-0', scheme.R, prefix);
  
  // Highlight it
  const edgeIds = ['sticker-F-1-2', 'sticker-R-1-0'];
  edgeIds.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// ============================================
// STEP 4: YELLOW CROSS (OLL - TOP LAYER)
// ============================================

// Complete yellow cross on top
function setYellowCross(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  // Yellow cross on top (4 yellow edges forming a +)
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);  // Top edge
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);  // Left edge
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);  // Right edge
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);  // Bottom edge
}

// Yellow cross highlighted
function setYellowCrossHighlighted(prefix = '', frontColor = 'green') {
  setYellowCross(prefix, frontColor);
  
  // Highlight the yellow cross
  const crossEdges = ['sticker-U-0-1', 'sticker-U-1-0', 'sticker-U-1-2', 'sticker-U-2-1'];
  crossEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 8px yellow)';
      sticker.style.strokeWidth = '2';
    }
  });
}

// Show F2L complete (starting point for yellow cross)
function setF2LComplete(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
}

// Yellow cross pattern: DOT (no yellow edges on top)
function setYellowCrossDot(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Only center is yellow, all edges are other colors (not yellow facing up)
  colorSticker('sticker-U-0-1', scheme.F, prefix);  // Front color on top
  colorSticker('sticker-U-1-0', scheme.L, prefix);  // Left color on top
  colorSticker('sticker-U-1-2', scheme.R, prefix);  // Right color on top
  colorSticker('sticker-U-2-1', scheme.B, prefix);  // Back color on top
  
  // Yellow center highlighted
  const center = document.getElementById(prefix ? `${prefix}-sticker-U-1-1` : 'sticker-U-1-1');
  if (center) {
    center.style.filter = 'drop-shadow(0 0 8px yellow)';
  }
}

// Yellow cross pattern: L SHAPE (2 adjacent yellow edges)
function setYellowCrossLShape(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // L shape: front and left edges are yellow
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);  // Front edge (yellow)
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);  // Left edge (yellow)
  
  // Other edges are not yellow
  colorSticker('sticker-U-0-1', scheme.B, prefix);       // Back edge (not yellow)
  colorSticker('sticker-U-1-2', scheme.R, prefix);       // Right edge (not yellow)
  
  // Highlight the L shape
  const lShapeEdges = ['sticker-U-2-1', 'sticker-U-1-0'];
  lShapeEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// Yellow cross pattern: LINE (2 opposite yellow edges)
function setYellowCrossLine(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Line shape: front and back edges are yellow (horizontal line)
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);  // Front edge (yellow)
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);  // Back edge (yellow)
  
  // Other edges are not yellow
  colorSticker('sticker-U-1-0', scheme.L, prefix);       // Left edge (not yellow)
  colorSticker('sticker-U-1-2', scheme.R, prefix);       // Right edge (not yellow)
  
  // Highlight the line
  const lineEdges = ['sticker-U-2-1', 'sticker-U-0-1'];
  lineEdges.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px yellow)';
    }
  });
}

// Show progression from dot to cross
function setYellowCrossProgression(prefix = '', stage = 0, frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Stage 0: Dot (no yellow)
  // Stage 1: L shape (2 adjacent)
  // Stage 2: Line (2 opposite)
  // Stage 3: Cross (all 4)
  
  if (stage === 0) {
    // Dot
    colorSticker('sticker-U-0-1', scheme.B, prefix);
    colorSticker('sticker-U-1-0', scheme.L, prefix);
    colorSticker('sticker-U-1-2', scheme.R, prefix);
    colorSticker('sticker-U-2-1', scheme.F, prefix);
  } else if (stage === 1) {
    // L shape
    colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
    colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
    colorSticker('sticker-U-0-1', scheme.B, prefix);
    colorSticker('sticker-U-1-2', scheme.R, prefix);
  } else if (stage === 2) {
    // Line
    colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
    colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
    colorSticker('sticker-U-1-0', scheme.L, prefix);
    colorSticker('sticker-U-1-2', scheme.R, prefix);
  } else if (stage === 3) {
    // Cross
    colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
    colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
    colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
    colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  }
}

// ============================================
// STEP 5: YELLOW FACE (OLL - ORIENT CORNERS)
// ============================================

// Complete yellow face on top (all yellow stickers facing up)
function setYellowFace(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  // Yellow cross
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  // Yellow corners
  colorSticker('sticker-U-0-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-0-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-2', COLORS.yellow, prefix);
}

// Yellow face highlighted
function setYellowFaceHighlighted(prefix = '', frontColor = 'green') {
  setYellowFace(prefix, frontColor);
  
  // Highlight the corners
  const corners = ['sticker-U-0-0', 'sticker-U-0-2', 'sticker-U-2-0', 'sticker-U-2-2'];
  corners.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 8px yellow)';
      sticker.style.strokeWidth = '2';
    }
  });
}

// Show yellow cross complete (starting point for yellow face)
function setYellowCrossComplete(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  // Yellow cross only
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  const scheme = getColorScheme(frontColor);
  
  // Corners not yet oriented (colors on top, not yellow)
  colorSticker('sticker-U-0-0', scheme.L, prefix);
  colorSticker('sticker-U-0-2', scheme.F, prefix);
  colorSticker('sticker-U-2-0', scheme.F, prefix);
  colorSticker('sticker-U-2-2', scheme.R, prefix);
}

// Fish pattern (1 corner correct, 3 to orient)
function setYellowFaceFish(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Yellow cross
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  // Fish pattern: back-left corner is yellow (correct)
  colorSticker('sticker-U-2-0', COLORS.yellow, prefix);
  
  // Other corners show other colors
  colorSticker('sticker-U-0-0', scheme.L, prefix);   // Front-left
  colorSticker('sticker-U-0-2', scheme.F, prefix);   // Front-right
  colorSticker('sticker-U-2-2', scheme.R, prefix);   // Back-right
  
  // Highlight the correct corner
  const correct = document.getElementById(prefix ? `${prefix}-sticker-U-2-0` : 'sticker-U-2-0');
  if (correct) {
    correct.style.filter = 'drop-shadow(0 0 8px lime)';
  }
}

// Sune pattern (2 adjacent corners correct)
function setYellowFaceSune(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Yellow cross
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  // Sune: back-left and back-right corners are yellow
  colorSticker('sticker-U-2-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-2', COLORS.yellow, prefix);
  
  // Front corners show other colors
  colorSticker('sticker-U-0-0', scheme.L, prefix);
  colorSticker('sticker-U-0-2', scheme.F, prefix);
  
  // Highlight the correct corners
  const correctCorners = ['sticker-U-2-0', 'sticker-U-2-2'];
  correctCorners.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px lime)';
    }
  });
}

// Antisune pattern (2 diagonal corners correct)
function setYellowFaceAntisune(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Yellow cross
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  // Antisune: front-left and back-right corners are yellow (diagonal)
  colorSticker('sticker-U-0-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-2', COLORS.yellow, prefix);
  
  // Other corners show other colors
  colorSticker('sticker-U-0-2', scheme.F, prefix);
  colorSticker('sticker-U-2-0', scheme.B, prefix);
  
  // Highlight the correct corners
  const correctCorners = ['sticker-U-0-0', 'sticker-U-2-2'];
  correctCorners.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px lime)';
    }
  });
}

// No corners correct (worst case, needs 2 algorithms)
function setYellowFaceNoCorners(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Yellow cross
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  // No corners yellow on top
  colorSticker('sticker-U-0-0', scheme.L, prefix);
  colorSticker('sticker-U-0-2', scheme.F, prefix);
  colorSticker('sticker-U-2-0', scheme.B, prefix);
  colorSticker('sticker-U-2-2', scheme.R, prefix);
  
  // Highlight all corners as needing work
  const allCorners = ['sticker-U-0-0', 'sticker-U-0-2', 'sticker-U-2-0', 'sticker-U-2-2'];
  allCorners.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px red)';
    }
  });
}

// ============================================
// STEP 6: (PLL - CORNERS)
// ============================================

// No corners correct (worst case, needs 2 algorithms)
function step6before(prefix = '', frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  buildFirstTwoLayers(prefix, frontColor);
  
  const scheme = getColorScheme(frontColor);
  
  // Yellow cross
  colorSticker('sticker-U-0-1', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-1-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-1', COLORS.yellow, prefix);
  
  // No corners yellow on top
  colorSticker('sticker-U-0-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-0-2', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-0', COLORS.yellow, prefix);
  colorSticker('sticker-U-2-2', COLORS.yellow, prefix);

  //


  
  // Highlight all corners as needing work
  const allCorners = ['sticker-U-0-0', 'sticker-U-0-2', 'sticker-U-2-0', 'sticker-U-2-2'];
  allCorners.forEach(id => {
    const fullId = prefix ? `${prefix}-${id}` : id;
    const sticker = document.getElementById(fullId);
    if (sticker) {
      sticker.style.filter = 'drop-shadow(0 0 6px red)';
    }
  });
}



if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    // Core utilities
    colorSticker,
    getColorScheme,
    setCenters,
    resetCubeGray,
    resetCubeWithCenters,
    cloneCubeWithUniqueIds,
    insertCubeInContainer,
    
    // Layer building
    buildWhiteCross,
    buildWhiteCorners,
    buildFirstLayer,
    buildMiddleLayer,
    buildFirstTwoLayers,
    
    // Step 1a: Daisy
    setDaisy,
    setDaisyHighlighted,
    setDaisyProgress,
    setScrambledWithWhiteEdges,
    
    // Step 1b: White Cross
    setWhiteCross,
    setWhiteCrossHighlighted,
    setDaisyToWhiteCrossTransition,
    setWhiteCrossIncorrect,
    
    // Step 2: White Corners
    setWhiteCorners,
    setWhiteCornersHighlighted,
    setWhiteCrossWithOneCorner,
    setCornerInTopWhiteRight,
    setCornerInTopWhiteFront,
    setCornerInTopWhiteUp,

    // Step 3: middle edges
    setMiddleLayerComplete,
    setMiddleLayerHighlighted,
    setFirstLayerComplete,
    setMiddleEdgeTopFacingFront,
    setMiddleEdgeTopFacingRight,
    setMiddleEdgeWithYellow,
    setMiddleEdgeStuck,
    setMiddleLayerOneEdge,

    // Step 4: Yellow Cross
    setYellowCross,
    setYellowCrossHighlighted,
    setF2LComplete,
    setYellowCrossDot,
    setYellowCrossLShape,
    setYellowCrossLine,
    setYellowCrossProgression,

    
  // Step 5: Yellow Face
    setYellowFace,
    setYellowFaceHighlighted,
    setYellowCrossComplete,
    setYellowFaceFish,
    setYellowFaceSune,
    setYellowFaceAntisune,
    setYellowFaceNoCorners,

  // Step 6: Permuter les coins jaunes (PLL)
    step6before,
    setAllCornersPositioned,
    setCornerPermutationDemo

    
  // Step 7: Permuter les arêtes jaunes (PLL)

    
  };
}