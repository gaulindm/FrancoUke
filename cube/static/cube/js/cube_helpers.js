/**
 * Cube Helpers - Fonctions utilitaires pour monter et gérer les cubes SVG
 * Compatible avec le système dual-template (right/left orientation)
 */

import { renderCube } from './cube_renderer.js';

/**
 * Monte un cube SVG dans un container avec l'orientation appropriée
 * 
 * @param {string} containerId - ID du div container où monter le cube
 * @param {Object|null} state - État du cube (JSON format)
 * @param {string} orientation - 'left' ou 'right' (défaut: 'right')
 * @returns {SVGElement|null} - L'élément SVG créé, ou null si erreur
 * 
 * @example
 * // Cube orientation droite (main droite)
 * mountCube("my-cube-container", cubeState, 'right');
 * 
 * @example
 * // Cube orientation gauche (main gauche)
 * mountCube("my-cube-container", cubeState, 'left');
 * 
 * @example
 * // Sans orientation (défaut = right)
 * mountCube("my-cube-container", cubeState);
 */
export function mountCube(containerId, state, orientation = 'right') {
  const container = document.getElementById(containerId);
  
  // Validation du container
  if (!container) {
    console.error(`[mountCube] Container '${containerId}' not found in DOM`);
    return null;
  }
  
  // Clear le container
  container.innerHTML = '';
  
  // Si pas d'état fourni, affiche un placeholder
  if (!state) {
    console.warn(`[mountCube] No state provided for container '${containerId}'`);
    container.innerHTML = `
      <div class="alert alert-secondary text-center py-4">
        <i class="bi bi-cube text-muted" style="font-size: 3rem;"></i>
        <p class="mb-0 mt-2 text-muted">Cube state not available</p>
        <small class="text-muted">Create the CubeState in your admin tool</small>
      </div>
    `;
    return null;
  }
  
  // Sélectionne le bon template selon l'orientation
  const templateId = orientation === 'left' ? 'cube-template-left' : 'cube-template-right';
  let template = document.getElementById(templateId);
  
  // Si le template n'existe pas, essaie des fallbacks
  if (!template) {
    console.warn(`[mountCube] Template '${templateId}' not found. Trying fallbacks...`);
    
    // Fallback 1: Essaie l'autre orientation
    const fallbackId = orientation === 'left' ? 'cube-template-right' : 'cube-template-left';
    template = document.getElementById(fallbackId);
    
    if (template) {
      console.warn(`[mountCube] Using fallback template: ${fallbackId}`);
    } else {
      // Fallback 2: Essaie l'ancien template (compatibilité)
      template = document.getElementById('cube-template');
      
      if (template) {
        console.warn('[mountCube] Using legacy cube-template (please update your _cube_svg.html)');
      } else {
        // Pas de template du tout - erreur critique
        console.error('[mountCube] No cube templates found! Make sure _cube_svg.html is included.');
        container.innerHTML = `
          <div class="alert alert-danger text-center py-3">
            <strong>Error:</strong> Cube templates not loaded
            <br><small>Include cube/partials/_cube_svg.html in your template</small>
          </div>
        `;
        return null;
      }
    }
  }
  
  // Clone et insère le template
  const clone = template.content.cloneNode(true);
  container.appendChild(clone);
  
  // Render l'état du cube
  const svg = container.querySelector("svg");
  
  if (!svg) {
    console.error(`[mountCube] SVG not found in cloned template for '${containerId}'`);
    return null;
  }
  
  // Vérifie que renderCube est disponible
  if (typeof renderCube !== 'function') {
    console.error('[mountCube] renderCube function not available. Import it first.');
    return null;
  }
  
  // Applique l'état
  try {
    renderCube(svg, state);
    console.log(`[mountCube] ✓ Cube mounted: ${containerId} (${orientation})`);
    return svg;
  } catch (error) {
    console.error(`[mountCube] Error rendering cube for '${containerId}':`, error);
    container.innerHTML = `
      <div class="alert alert-danger text-center py-3">
        <strong>Render Error:</strong> ${error.message}
      </div>
    `;
    return null;
  }
}

/**
 * Monte plusieurs cubes à partir d'une liste de configurations
 * 
 * @param {Array} cubeConfigs - Liste de {id, state, orientation}
 * @returns {Array<SVGElement>} - Liste des SVG créés
 * 
 * @example
 * mountMultipleCubes([
 *   { id: 'cube-1', state: state1, orientation: 'right' },
 *   { id: 'cube-2', state: state2, orientation: 'left' },
 *   { id: 'cube-3', state: state3 } // défaut = right
 * ]);
 */
export function mountMultipleCubes(cubeConfigs) {
  if (!Array.isArray(cubeConfigs)) {
    console.error('[mountMultipleCubes] Expected an array of cube configs');
    return [];
  }
  
  const results = [];
  
  cubeConfigs.forEach(config => {
    if (!config.id) {
      console.warn('[mountMultipleCubes] Config missing id, skipping:', config);
      return;
    }
    
    const svg = mountCube(
      config.id,
      config.state,
      config.orientation || 'right'
    );
    
    if (svg) {
      results.push(svg);
    }
  });
  
  console.log(`[mountMultipleCubes] ✓ Mounted ${results.length}/${cubeConfigs.length} cubes`);
  return results;
}

/**
 * Détecte automatiquement l'orientation basée sur un data-attribute
 * Utile pour les templates dynamiques
 * 
 * @param {string} containerId - ID du container
 * @param {Object} state - État du cube
 * @returns {SVGElement|null}
 * 
 * @example
 * // HTML: <div id="my-cube" data-orientation="left"></div>
 * mountCubeAuto("my-cube", cubeState);
 */
export function mountCubeAuto(containerId, state) {
  const container = document.getElementById(containerId);
  
  if (!container) {
    console.error(`[mountCubeAuto] Container '${containerId}' not found`);
    return null;
  }
  
  // Récupère l'orientation depuis le data-attribute
  const orientation = container.dataset.orientation || 'right';
  
  return mountCube(containerId, state, orientation);
}

/**
 * Vérifie que tous les templates nécessaires sont chargés
 * Utile pour le debugging
 * 
 * @returns {Object} - Status de chaque template
 */
export function checkTemplatesLoaded() {
  const status = {
    'cube-template-right': !!document.getElementById('cube-template-right'),
    'cube-template-left': !!document.getElementById('cube-template-left'),
    'cube-template (legacy)': !!document.getElementById('cube-template'),
  };
  
  console.log('[checkTemplatesLoaded] Template status:', status);
  
  const allLoaded = status['cube-template-right'] && status['cube-template-left'];
  
  if (!allLoaded) {
    console.warn('[checkTemplatesLoaded] ⚠️ Some templates are missing!');
    console.warn('Make sure to include: {% include "cube/partials/_cube_svg.html" %}');
  } else {
    console.log('[checkTemplatesLoaded] ✓ All templates loaded');
  }
  
  return status;
}

/**
 * Helper pour extraire l'orientation d'un CubeState Django
 * À utiliser côté template
 * 
 * @param {Object} cubeState - Objet CubeState Django (serialized)
 * @returns {string} - 'left' ou 'right'
 */
export function getOrientation(cubeState) {
  if (!cubeState) {
    return 'right';
  }
  
  // Si l'objet a une propriété hand_orientation
  if (cubeState.hand_orientation) {
    return cubeState.hand_orientation;
  }
  
  // Sinon, détecte basé sur l'algorithme
  if (cubeState.algorithm) {
    const alg = cubeState.algorithm.toUpperCase();
    const lCount = (alg.match(/L['2]?/g) || []).length;
    const rCount = (alg.match(/R['2]?/g) || []).length;
    
    return lCount > rCount ? 'left' : 'right';
  }
  
  // Par défaut
  return 'right';
}

// Export default pour import simplifié
export default {
  mountCube,
  mountMultipleCubes,
  mountCubeAuto,
  checkTemplatesLoaded,
  getOrientation,
};
