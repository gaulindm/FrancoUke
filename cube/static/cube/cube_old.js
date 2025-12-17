// cube.js - Fonctions pour visualiser l'étape de la marguerite

// Couleurs standard du cube
const COLORS = {
  white: '#FFFFFF',
  yellow: '#FFD700',
  green: '#00FF00',
  blue: '#0000FF',
  red: '#FF0000',
  orange: '#FFA500',
  gray: '#CCCCCC',
  highlight: '#FFFF00'
};

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
  R: 'red',      // Right
  B: 'blue',     // Back
  L: 'orange'    // Left
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
      R: COLORS.red,
      B: COLORS.blue,
      L: COLORS.orange
    },
    'red': {
      F: COLORS.red,
      R: COLORS.blue,
      B: COLORS.orange,
      L: COLORS.green
    },
    'blue': {
      F: COLORS.blue,
      R: COLORS.orange,
      B: COLORS.green,
      L: COLORS.red
    },
    'orange': {
      F: COLORS.orange,
      R: COLORS.green,
      B: COLORS.red,
      L: COLORS.blue
    }
  };
  
  const scheme = rotations[frontColor] || rotations['green'];
  colorSticker('sticker-F-1-1', scheme.F, prefix);
  colorSticker('sticker-R-1-1', scheme.R, prefix);
  colorSticker('sticker-B-1-1', scheme.B, prefix);
  colorSticker('sticker-L-1-1', scheme.L, prefix);
}

// Convenience functions for specific orientations
function setCentersGreenFront(prefix = '') {
  setCenters(prefix, 'green');
}

function setCentersRedFront(prefix = '') {
  setCenters(prefix, 'red');
}

function setCentersBlueFront(prefix = '') {
  setCenters(prefix, 'blue');
}

function setCentersOrangeFront(prefix = '') {
  setCenters(prefix, 'orange');
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
  colorSticker('sticker-F-0-1', COLORS.green, prefix);   // Front edge
  colorSticker('sticker-R-0-1', COLORS.red, prefix);     // Right edge
  colorSticker('sticker-B-0-1', COLORS.blue, prefix);    // Back edge
  colorSticker('sticker-L-0-1', COLORS.orange, prefix);  // Left edge
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
      sticker.style.filter = 'drop-shadow(0 0 8px yellow)';
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
  
  // Add some colored EDGES for realism (no corners!)
  colorSticker('sticker-F-0-1', COLORS.red, prefix);     // Front face, top edge
  colorSticker('sticker-F-2-1', COLORS.blue, prefix);    // Front face, bottom edge
  colorSticker('sticker-R-0-1', COLORS.green, prefix);   // Right face, top edge
  colorSticker('sticker-R-1-2', COLORS.orange, prefix);  // Right face, right edge
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
  
  // Get the color scheme for current orientation
  const rotations = {
    'green': { F: COLORS.green, R: COLORS.red, B: COLORS.blue, L: COLORS.orange },
    'red': { F: COLORS.red, R: COLORS.blue, B: COLORS.orange, L: COLORS.green },
    'blue': { F: COLORS.blue, R: COLORS.orange, B: COLORS.green, L: COLORS.red },
    'orange': { F: COLORS.orange, R: COLORS.green, B: COLORS.red, L: COLORS.blue }
  };
  const scheme = rotations[frontColor] || rotations['green'];
  
  // White cross on bottom (4 white edges forming a +)
  colorSticker('sticker-D-0-1', COLORS.white, prefix);  // Top edge
  colorSticker('sticker-D-1-0', COLORS.white, prefix);  // Left edge
  colorSticker('sticker-D-1-2', COLORS.white, prefix);  // Right edge
  colorSticker('sticker-D-2-1', COLORS.white, prefix);  // Bottom edge
  
  // Matching side colors (the "correct" cross)
  colorSticker('sticker-F-2-1', scheme.F, prefix);      // Front bottom edge matches front center
  colorSticker('sticker-R-2-1', scheme.R, prefix);      // Right bottom edge matches right center
  colorSticker('sticker-B-2-1', scheme.B, prefix);      // Back bottom edge matches back center
  colorSticker('sticker-L-2-1', scheme.L, prefix);      // Left bottom edge matches left center
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

// Show transition from daisy to white cross
function setDaisyToWhiteCrossTransition(prefix = '', edgeNumber = 0, frontColor = 'green') {
  resetCubeWithCenters(prefix, frontColor);
  
  // Start with daisy (petals still on top)
  const remainingPetals = [];
  const flippedEdges = [];
  
  // Define which edges have been flipped based on edgeNumber (0-4)
  const petalPositions = [
    { top: 'sticker-U-2-1', bottom: 'sticker-D-0-1', side: 'sticker-F-2-1' },  // Front edge
    { top: 'sticker-U-1-2', bottom: 'sticker-D-1-2', side: 'sticker-R-2-1' },  // Right edge
    { top: 'sticker-U-0-1', bottom: 'sticker-D-2-1', side: 'sticker-B-2-1' },  // Back edge
    { top: 'sticker-U-1-0', bottom: 'sticker-D-1-0', side: 'sticker-L-2-1' }   // Left edge
  ];
  
  const rotations = {
    'green': { F: COLORS.green, R: COLORS.red, B: COLORS.blue, L: COLORS.orange },
    'red': { F: COLORS.red, R: COLORS.blue, B: COLORS.orange, L: COLORS.green },
    'blue': { F: COLORS.blue, R: COLORS.orange, B: COLORS.green, L: COLORS.red },
    'orange': { F: COLORS.orange, R: COLORS.green, B: COLORS.red, L: COLORS.blue }
  };
  const scheme = rotations[frontColor] || rotations['green'];
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
  colorSticker('sticker-F-2-1', COLORS.blue, prefix);    // Wrong! Should match center
  colorSticker('sticker-R-2-1', COLORS.orange, prefix);  // Wrong!
  colorSticker('sticker-B-2-1', COLORS.green, prefix);   // Wrong!
  colorSticker('sticker-L-2-1', COLORS.red, prefix);     // Wrong!
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    setDaisy,
    setDaisyHighlighted,
    setDaisyProgress,
    setScrambledWithWhiteEdges,
    insertCubeInContainer,
    cloneCubeWithUniqueIds
  };
}