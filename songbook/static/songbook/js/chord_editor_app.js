// static/js/chord_editor_app.js
// Make sure this file is collected as static and referenced in the template.

(function () {
    // Utilities: read CSRF token from cookie (standard Django pattern)
    function getCookie(name) {
      const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
      return v ? v.pop() : '';
    }
  
    const CSRF_TOKEN = getCookie('csrftoken');
  
    // Global state
    let CHORDS = {}; // full dictionary fetched from backend
    let currentInstrument = null;
    let currentChordName = null;
    let currentVariationIndex = null;
  
    // DOM refs
    const instrumentSelect = document.getElementById('instrument-select');
    const chordListDiv = document.getElementById('chord-list');
    const chordNameH2 = document.getElementById('chord-name');
    const variationListDiv = document.getElementById('variation-list');
    const addChordBtn = document.getElementById('add-chord-btn');
    const addVariationBtn = document.getElementById('add-variation-btn');
    const editorPanel = document.getElementById('editor-panel');
    const fretEditorContainer = document.getElementById('fret-editor-container');
    const previewDiv = document.getElementById('preview');
    const saveBtn = document.getElementById('save-btn');
    const deleteVariationBtn = document.getElementById('delete-variation-btn');
  
    // API endpoints exposed by template
    const API_GET = window.API_GET || '/api/chords/';
    const API_SAVE = window.API_SAVE || '/api/chords/save/';
  
    // INITIAL LOAD
    async function init() {
      await loadAllChords();
      populateInstrumentSelect();
      instrumentSelect.addEventListener('change', onInstrumentChange);
      addChordBtn.addEventListener('click', onAddChord);
      addVariationBtn.addEventListener('click', onAddVariation);
      saveBtn.addEventListener('click', onSaveAll);
      deleteVariationBtn.addEventListener('click', onDeleteVariation);
      // select first instrument if present
      if (instrumentSelect.options.length) {
        instrumentSelect.selectedIndex = 0;
        onInstrumentChange();
      }
    }
  
    async function loadAllChords() {
      try {
        const r = await fetch(API_GET);
        if (!r.ok) throw new Error('Failed to load chords: ' + r.status);
        CHORDS = await r.json();
      } catch (err) {
        alert('Error loading chord data: ' + err);
        CHORDS = {};
      }
    }
  
    function populateInstrumentSelect() {
      instrumentSelect.innerHTML = '';
      Object.keys(CHORDS).forEach(instr => {
        const opt = document.createElement('option');
        opt.value = instr;
        opt.textContent = instr;
        instrumentSelect.appendChild(opt);
      });
    }
  
    function onInstrumentChange() {
      currentInstrument = instrumentSelect.value;
      renderChordList();
      clearSelection();
    }
  
    function renderChordList() {
      chordListDiv.innerHTML = '';
      const instrumentMap = CHORDS[currentInstrument] || [];
      // CHORDS structure: instrument: [ { name, variations: [...] }, ... ]
      instrumentMap.forEach((chord, idx) => {
        const el = document.createElement('div');
        el.className = 'chord-row';
        el.style.padding = '6px';
        el.style.borderBottom = '1px solid #eee';
        el.style.cursor = 'pointer';
        el.textContent = chord.name || '(unnamed)';
        el.onclick = () => selectChord(idx);
        chordListDiv.appendChild(el);
      });
    }
  
    function selectChord(index) {
      const instrumentMap = CHORDS[currentInstrument] || [];
      const chord = instrumentMap[index];
      if (!chord) return;
      currentChordName = chord.name;
      currentVariationIndex = null;
      chordNameH2.textContent = chord.name;
      renderVariationList(chord);
      addVariationBtn.style.display = 'inline-block';
      editorPanel.style.display = 'none';
    }
  
    function renderVariationList(chord) {
      variationListDiv.innerHTML = '';
      (chord.variations || []).forEach((v, i) => {
        const el = document.createElement('div');
        el.style.padding = '6px';
        el.style.border = '1px solid #ddd';
        el.style.marginBottom = '6px';
        el.style.display = 'flex';
        el.style.justifyContent = 'space-between';
        el.style.alignItems = 'center';
  
        const left = document.createElement('div');
        left.textContent = `Variation ${i+1} (${formatPositions(v.positions)})`;
        left.style.cursor = 'pointer';
        left.onclick = () => editVariation(i);
  
        const right = document.createElement('div');
        const previewBtn = document.createElement('button');
        previewBtn.textContent = 'Preview';
        previewBtn.onclick = (ev) => {
          ev.stopPropagation();
          renderVariationPreview(v);
        };
  
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.style.marginLeft = '6px';
        deleteBtn.onclick = (ev) => {
          ev.stopPropagation();
          if (!confirm('Delete variation?')) return;
          chord.variations.splice(i, 1);
          renderChordList();
          selectChord(CHORDS[currentInstrument].findIndex(c => c.name === chord.name));
        };
  
        right.appendChild(previewBtn);
        right.appendChild(deleteBtn);
  
        el.appendChild(left);
        el.appendChild(right);
        variationListDiv.appendChild(el);
      });
    }
  
    function formatPositions(positions) {
      if (!positions) return '';
      return positions.map(p => String(p)).join(',');
    }
  
    function editVariation(index) {
      currentVariationIndex = index;
      const chord = CHORDS[currentInstrument].find(c => c.name === currentChordName);
      const variation = chord.variations[index];
      buildFretEditor(variation);
      renderVariationPreview(variation);
      editorPanel.style.display = 'block';
    }
  
    function buildFretEditor(variation) {
      // Variation expected shape: { positions: [ ... ], baseFret: n, fingers?: [] }
      fretEditorContainer.innerHTML = '';
  
      const pos = variation.positions || [];
      const table = document.createElement('table');
      table.style.borderCollapse = 'collapse';
  
      // For each string (row)
      pos.forEach((val, stringIdx) => {
        const tr = document.createElement('tr');
  
        // show string label
        const tdLabel = document.createElement('td');
        tdLabel.textContent = `S${stringIdx+1}`;
        tdLabel.style.padding = '4px 8px';
        tr.appendChild(tdLabel);
  
        // choices: 'x', 0, 1..6
        const choices = ['x', 0, 1, 2, 3, 4, 5, 6];
        choices.forEach(choice => {
          const td = document.createElement('td');
          td.textContent = choice;
          td.style.padding = '6px';
          td.style.border = '1px solid #ddd';
          td.style.minWidth = '30px';
          td.style.textAlign = 'center';
          if (String(choice) === String(val)) {
            td.style.background = '#007bff';
            td.style.color = '#fff';
          }
  
          td.onclick = () => {
            variation.positions[stringIdx] = choice;
            buildFretEditor(variation);
            renderVariationPreview(variation);
          };
  
          tr.appendChild(td);
        });
  
        table.appendChild(tr);
      });
  
      // baseFret editor row
      const trBase = document.createElement('tr');
      const tdBaseLabel = document.createElement('td');
      tdBaseLabel.textContent = 'Base';
      tdBaseLabel.style.padding = '4px 8px';
      trBase.appendChild(tdBaseLabel);
  
      [1,2,3,4,5,6].forEach(b => {
        const td = document.createElement('td');
        td.textContent = b;
        td.style.padding = '6px';
        td.style.border = '1px solid #ddd';
        td.style.textAlign = 'center';
        if ((variation.baseFret || 1) === b) {
          td.style.background = '#28a745';
          td.style.color = '#fff';
        }
        td.onclick = () => {
          variation.baseFret = b;
          buildFretEditor(variation);
          renderVariationPreview(variation);
        };
        trBase.appendChild(td);
      });
      table.appendChild(trBase);
  
      fretEditorContainer.appendChild(table);
    }
  
    function renderVariationPreview(variation) {
      previewDiv.innerHTML = '';
      try {
        // Use Raphael chord renderer - expects container element and variation obj
        // Variation may just have positions/baseFret - that's fine.
        new Raphael.chord.Chord(previewDiv, variation, currentChordName);
      } catch (e) {
        previewDiv.textContent = 'Preview render error: ' + e;
      }
    }
  
    async function onAddChord() {
      const name = prompt('New chord name (e.g., Gmaj7):');
      if (!name) return;
      // default variation (4 strings) fallback - if instrument has chords, copy string count otherwise 4
      const instrumentList = CHORDS[currentInstrument] || [];
      const defaultStrings = (() => {
        if (instrumentList.length && instrumentList[0].variations && instrumentList[0].variations[0]) {
          return instrumentList[0].variations[0].positions.length;
        }
        return 4;
      })();
  
      const newChord = {
        name: name.trim(),
        variations: [{
          positions: Array.from({length: defaultStrings}).map(() => 'x'),
          baseFret: 1
        }]
      };
  
      CHORDS[currentInstrument].push(newChord);
      renderChordList();
      // auto-select new chord
      selectChord(CHORDS[currentInstrument].length - 1);
    }
  
    function onAddVariation() {
      const chord = CHORDS[currentInstrument].find(c => c.name === currentChordName);
      if (!chord) return;
      const defaultLen = chord.variations && chord.variations[0] ? chord.variations[0].positions.length : 4;
      chord.variations.push({
        positions: Array.from({length: defaultLen}).map(() =>'x'),
        baseFret: 1
      });
      renderVariationList(chord);
    }
  
    async function onSaveAll() {
      try {
        const resp = await fetch(API_SAVE, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
          },
          body: JSON.stringify(CHORDS)
        });
        const data = await resp.json();
        if (!resp.ok) {
          alert('Save failed: ' + (data.error || resp.status));
        } else {
          alert('Saved: ' + (data.saved || []).join(', '));
          // reload to pick up any formatting changes
          await loadAllChords();
          populateInstrumentSelect();
          // reselect current instrument if exists
          if (CHORDS[currentInstrument]) {
            renderChordList();
          }
        }
      } catch (e) {
        alert('Network error saving chords: ' + e);
      }
    }
  
    function onDeleteVariation() {
      if (currentVariationIndex === null) {
        alert('No variation selected');
        return;
      }
      const chord = CHORDS[currentInstrument].find(c => c.name === currentChordName);
      if (!chord) return;
      if (!confirm('Delete this variation?')) return;
      chord.variations.splice(currentVariationIndex, 1);
      renderVariationList(chord);
      editorPanel.style.display = 'none';
    }
  
    function clearSelection() {
      currentChordName = null;
      currentVariationIndex = null;
      chordNameH2.textContent = 'Select a chord';
      variationListDiv.innerHTML = '';
      addVariationBtn.style.display = 'none';
      editorPanel.style.display = 'none';
    }
  
    // Expose small helpers for console debugging
    window._CHORDS = CHORDS;
    window._reloadChordEditor = async () => {
      await loadAllChords();
      populateInstrumentSelect();
    };
  
    // start
    init();
  })();
  