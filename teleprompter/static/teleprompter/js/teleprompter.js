/* Teleprompter JS
   - parses [Chord]inline lyrics
   - renders chords above lyrics tokens
   - supports transpose, auto-scroll, adjustable speed & font size
   - draws simple chord diagrams (SVG) for common chords
*/

(function(){
    // --- utilities ---
    function $(sel, root=document) { return root.querySelector(sel); }
    function $all(sel, root=document) { return Array.from(root.querySelectorAll(sel)); }
  
    // --- parsing chorded lines ---
    function parseChordedLines(text){
      text = text.replace(/\r\n/g, '\n');
      const lines = text.split('\n');
      return lines.map(parseLine);
    }
  
    function parseLine(line){
      // returns array of {chord: string|null, text: string}
      const matches = Array.from(line.matchAll(/\[([^\]]+)\]/g));
      const tokens = [];
      if (matches.length === 0) {
        tokens.push({chord: null, text: line.length? line : ' '});
        return tokens;
      }
      let lastIndex = 0;
      for (let i=0; i<matches.length; i++){
        const m = matches[i];
        const start = m.index;
        if (start > lastIndex){
          const pre = line.substring(lastIndex, start);
          if (pre.length) tokens.push({chord: null, text: pre});
        }
        const chord = m[1].trim();
        const nextStart = (i+1 < matches.length) ? matches[i+1].index : line.length;
        const textForChord = line.substring(m.index + m[0].length, nextStart);
        tokens.push({chord: chord || null, text: textForChord.length? textForChord : ' '});
        lastIndex = nextStart;
      }
      if (lastIndex < line.length){
        const tail = line.substring(lastIndex);
        if (tail.length) tokens.push({chord: null, text: tail});
      }
      return tokens;
    }
  
    // --- transpose utilities ---
    const SHARP_NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
    const FLAT_TO_SHARP = {'Db':'C#','Eb':'D#','Gb':'F#','Ab':'G#','Bb':'A#'};
    function normalizeNote(note){
      // note like 'Bb' -> 'A#' ; uppercase
      if (!note) return note;
      if (note.length === 1) return note.toUpperCase();
      const up = note[0].toUpperCase() + (note[1] || '');
      if (FLAT_TO_SHARP[up]) return FLAT_TO_SHARP[up];
      return up.replace('♭','b').replace('♯','#');
    }
  
    function transposeSingleName(name, steps){
      // name example: "F#", "Bb", "E"
      let norm = normalizeNote(name);
      let idx = SHARP_NOTES.indexOf(norm);
      if (idx === -1) return name; // unknown, give up
      const newIdx = (idx + steps + 1200) % 12;
      return SHARP_NOTES[newIdx];
    }
  
    function transposeChordString(chordStr, steps){
      // Handles chords with modifiers and slash bass like "F#m7/G#"
      if (!chordStr) return chordStr;
      const parts = chordStr.split('/');
      const transParts = parts.map(p => {
        // root is first 1 or 2 chars (e.g., A, A#, Bb)
        const m = p.match(/^([A-G][b#]?)/i);
        if (!m) return p; // can't parse
        const root = m[1];
        const rest = p.slice(root.length);
        const newRoot = transposeSingleName(root, steps);
        return newRoot + rest;
      });
      return transParts.join('/');
    }
  
    // --- chord diagram shapes (strings 6 -> 1) ---
    // 'x' = muted, 0 = open, numbers = fret
    const CHORD_SHAPES = {
      "C":  { strings: ['x',3,2,0,1,0], baseFret:0 },
      "G":  { strings: [3,2,0,0,0,3], baseFret:0 },
      "D":  { strings: ['x','x',0,2,3,2], baseFret:0 },
      "A":  { strings: ['x',0,2,2,2,0], baseFret:0 },
      "E":  { strings: [0,2,2,1,0,0], baseFret:0 },
      "Am": { strings: ['x',0,2,2,1,0], baseFret:0 },
      "Em": { strings: [0,2,2,0,0,0], baseFret:0 },
      "F":  { strings: [1,3,3,2,1,1], baseFret:1 }, // barre F
      "Bm": { strings: ['x',2,4,4,3,2], baseFret:0 },
      "D7": { strings: ['x','x',0,2,1,2], baseFret:0 }
      // add more shapes as you want
    };
  
    // draws a small svg chord diagram inside container element
    function drawChordDiagram(container, chordName){
      container.innerHTML = '';
      const title = document.createElement('div');
      title.textContent = chordName;
      title.style.fontWeight = "700";
      title.style.marginBottom = "6px";
      container.appendChild(title);
  
      // find shape by chord root (and minor)
      const m = chordName.match(/^([A-G][b#]?)(.*)$/i);
      const root = m ? m[1].toUpperCase().replace('B#','C') : null;
      const modifier = m ? m[2] : '';
      const normalizedRoot = FLAT_TO_SHARP[root] || root;
      const candidates = [
        normalizedRoot + (modifier && modifier.trim().startsWith('m') ? 'm' : ''),
        normalizedRoot
      ];
      let shape = null;
      for (let c of candidates) {
        if (CHORD_SHAPES[c]) { shape = CHORD_SHAPES[c]; break; }
      }
  
      if (!shape){
        const fallback = document.createElement('div');
        fallback.textContent = 'no diagram';
        fallback.style.opacity = '0.7';
        container.appendChild(fallback);
        return;
      }
  
      const w = 80, h = 110, padding = 8;
      const svgNS = "http://www.w3.org/2000/svg";
      const svg = document.createElementNS(svgNS,'svg');
      svg.setAttribute('width', w);
      svg.setAttribute('height', h);
      svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
      svg.style.display = 'block';
      svg.style.margin = '2px auto';
      container.appendChild(svg);
  
      const cols = 6;
      const rows = 5; // number of frets visible
      const topY = 20;
      const leftX = 12;
      const rightX = w - 12;
      const fretSpacing = (h - topY - padding) / rows;
      const stringSpacing = (rightX - leftX) / (cols - 1);
  
      // draw strings (vertical)
      for (let i = 0; i < cols; i++){
        const x = leftX + i * stringSpacing;
        const line = document.createElementNS(svgNS,'line');
        line.setAttribute('x1', x);
        line.setAttribute('y1', topY);
        line.setAttribute('x2', x);
        line.setAttribute('y2', topY + fretSpacing * rows);
        line.setAttribute('stroke', '#ddd');
        line.setAttribute('stroke-width', 1.2);
        svg.appendChild(line);
      }
  
      // draw frets (horizontal)
      for (let r = 0; r <= rows; r++){
        const y = topY + r * fretSpacing;
        const line = document.createElementNS(svgNS,'line');
        line.setAttribute('x1', leftX);
        line.setAttribute('y1', y);
        line.setAttribute('x2', rightX);
        line.setAttribute('y2', y);
        line.setAttribute('stroke', r===0 ? '#fff' : '#ccc');
        line.setAttribute('stroke-width', r===0?2:1);
        svg.appendChild(line);
      }
  
      // find minimum displayed fret (for barre and high chords)
      const s = shape.strings;
      const fretNumbers = s.map(v => typeof v === 'number' && v>0 ? v : null).filter(Boolean);
      const minFret = shape.baseFret || (fretNumbers.length ? Math.min(...fretNumbers) : 0);
      const displayOffset = Math.max(0, minFret <= 1 ? 1 : minFret);
  
      // draw dots (strings are 6->1 in our shape array)
      for (let i=0;i<6;i++){
        const val = shape.strings[i];
        const stringIndex = i; // shape strings array is 6->1
        const x = leftX + stringIndex * stringSpacing;
        if (val === 'x' || val === 'X') {
          const text = document.createElementNS(svgNS,'text');
          text.setAttribute('x', x);
          text.setAttribute('y', topY - 6);
          text.setAttribute('text-anchor','middle');
          text.setAttribute('font-size', 10);
          text.setAttribute('fill', '#fff');
          text.textContent = 'x';
          svg.appendChild(text);
        } else if (val === 0) {
          const text = document.createElementNS(svgNS,'text');
          text.setAttribute('x', x);
          text.setAttribute('y', topY - 6);
          text.setAttribute('text-anchor','middle');
          text.setAttribute('font-size', 10);
          text.setAttribute('fill', '#fff');
          text.textContent = 'o';
          svg.appendChild(text);
        } else if (typeof val === 'number') {
          const fret = val - (displayOffset - 1);
          const y = topY + fret * fretSpacing - fretSpacing/2;
          const circle = document.createElementNS(svgNS,'circle');
          circle.setAttribute('cx', x);
          circle.setAttribute('cy', y);
          circle.setAttribute('r', 6);
          circle.setAttribute('fill', '#ffd166');
          svg.appendChild(circle);
        }
      }
  
      // If baseFret > 1 show "3fr" label
      if (shape.baseFret && shape.baseFret > 1){
        const lbl = document.createElementNS(svgNS,'text');
        lbl.setAttribute('x', rightX + 6);
        lbl.setAttribute('y', topY + fretSpacing/2 + 4);
        lbl.setAttribute('font-size', 10);
        lbl.setAttribute('fill', '#ddd');
        lbl.textContent = shape.baseFret + "fr";
        svg.appendChild(lbl);
      }
    }
  
    // --- render UI & behavior ---
    function renderSong(songObj){
      const parsed = parseChordedLines(songObj.lyrics || '');
      const container = $('#lyrics-container');
      container.innerHTML = '';
  
      parsed.forEach((lineTokens) => {
        const lineEl = document.createElement('div');
        lineEl.className = 'line';
        lineTokens.forEach(tok => {
          // preserve leading/trailing spaces — use tokenization with tokens as inline-blocks
          const token = document.createElement('span');
          token.className = 'token';
          const chordSpan = document.createElement('span');
          chordSpan.className = 'chord';
          chordSpan.textContent = tok.chord || '';
          if (!tok.chord) chordSpan.style.visibility = 'hidden';
          const lyricSpan = document.createElement('span');
          lyricSpan.className = 'lyric';
          lyricSpan.textContent = tok.text || ' ';
          // if lyric is all spaces, preserve them
          if (/^\s*$/.test(tok.text)) lyricSpan.textContent = tok.text.replace(/ /g, '\u00A0');
  
          token.appendChild(chordSpan);
          token.appendChild(lyricSpan);
          lineEl.appendChild(token);
        });
        container.appendChild(lineEl);
      });
  
      // collect unique chords to show diagrams
      const chordsSet = new Set();
      parsed.flat().forEach(tok => { if (tok.chord) chordsSet.add(tok.chord.trim()); });
      renderChordDiagrams(Array.from(chordsSet));
    }
  
    function renderChordDiagrams(chordsArray){
      const parent = $('#chords-diagrams');
      parent.innerHTML = '';
      if (!chordsArray.length){
        parent.style.display = 'none';
        return;
      }
      parent.style.display = 'flex';
      chordsArray.forEach(ch => {
        const box = document.createElement('div');
        box.className = 'diagram';
        drawChordDiagram(box, ch);
        parent.appendChild(box);
      });
    }
  
    // --- scrolling engine ---
    let reqId = null;
    let lastTime = null;
    let scrollSpeed = 60; // px per sec
    let isPlaying = false;
  
    function startAutoScroll(){
      if (isPlaying) return;
      isPlaying = true;
      lastTime = performance.now();
      function step(ts){
        if (!isPlaying) { reqId = null; return; }
        const dt = ts - lastTime;
        lastTime = ts;
        const dy = (scrollSpeed) * dt / 1000;
        $('#lyrics-container').scrollTop += dy;
        reqId = requestAnimationFrame(step);
      }
      reqId = requestAnimationFrame(step);
    }
  
    function stopAutoScroll(){
      isPlaying = false;
      if (reqId) cancelAnimationFrame(reqId);
      reqId = null;
    }
  
    // --- transpose live ---
    function transposeDisplayed(amount){
      const container = $('#lyrics-container');
      const chordEls = container.querySelectorAll('.chord');
      chordEls.forEach(el => {
        const original = el.getAttribute('data-original') || el.textContent;
        if (!el.getAttribute('data-original')) el.setAttribute('data-original', el.textContent);
        el.textContent = transposeChordString(original, amount);
        el.style.visibility = el.textContent ? 'visible' : 'hidden';
      });
  
      // update diagrams
      const chordsSet = new Set();
      const parsed = parseChordedLines(SONG.lyrics || '');
      parsed.flat().forEach(tok => {
        if (tok.chord) chordsSet.add(transposeChordString(tok.chord, amount));
      });
      renderChordDiagrams(Array.from(chordsSet));
    }
  
    // --- initialization and controls ---
    function init(){
      document.title = "Teleprompter — " + SONG.title;
      $('#song-title').textContent = SONG.title;
  
      // initial render
      renderSong(SONG);
  
      // controls
      const speedInput = $('#speed');
      const speedValue = $('#speed-value');
      speedValue.textContent = speedInput.value;
      scrollSpeed = parseInt(speedInput.value, 10);
  
      speedInput.addEventListener('input', (e) => {
        scrollSpeed = parseInt(e.target.value, 10);
        speedValue.textContent = e.target.value;
      });
  
      $('#btn-play').addEventListener('click', ()=>{
        startAutoScroll();
      });
      $('#btn-stop').addEventListener('click', ()=>{
        stopAutoScroll();
      });
  
      // font size control
      const fontInput = $('#font-size');
      const fontValue = $('#font-value');
      fontValue.textContent = fontInput.value;
      $('.lyric', document).forEach?.(el => {}); // noop to quiet unused
      fontInput.addEventListener('input', (e)=>{
        const v = e.target.value;
        fontValue.textContent = v;
        $all('.lyric').forEach(el => el.style.fontSize = `${v}px`);
      });
  
      // transpose
      let transposeAmount = Number(SONG.initialTranspose) || 0;
      $('#transpose-value').textContent = transposeAmount;
      $('#transpose-up').addEventListener('click', ()=>{
        transposeAmount += 1;
        $('#transpose-value').textContent = transposeAmount;
        transposeDisplayed(transposeAmount);
      });
      $('#transpose-down').addEventListener('click', ()=>{
        transposeAmount -= 1;
        $('#transpose-value').textContent = transposeAmount;
        transposeDisplayed(transposeAmount);
      });
  
      // fullscreen
      $('#fullscreen').addEventListener('click', ()=>{
        const el = document.documentElement;
        if (el.requestFullscreen) el.requestFullscreen();
        else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
      });
  
      // keyboard shortcuts
      document.addEventListener('keydown', (e)=>{
        if (e.code === 'Space') { e.preventDefault(); isPlaying? stopAutoScroll() : startAutoScroll(); }
        if (e.code === 'ArrowUp') { speedInput.value = Math.min(300, Number(speedInput.value) + 10); speedInput.dispatchEvent(new Event('input')); }
        if (e.code === 'ArrowDown') { speedInput.value = Math.max(10, Number(speedInput.value) - 10); speedInput.dispatchEvent(new Event('input')); }
        if (e.key === '+') { $('#transpose-up').click(); }
        if (e.key === '-') { $('#transpose-down').click(); }
      });
  
      // make sure tokens preserve original chord text for re-transpose
      $all('.chord').forEach(el => { el.setAttribute('data-original', el.textContent); });
  
      // initial transpose if any
      if (SONG.initialTranspose && Number(SONG.initialTranspose) !== 0){
        transposeDisplayed(Number(SONG.initialTranspose));
        $('#transpose-value').textContent = Number(SONG.initialTranspose);
      }
    }
  
    // run when DOM ready
    document.addEventListener('DOMContentLoaded', init);
  })();
  