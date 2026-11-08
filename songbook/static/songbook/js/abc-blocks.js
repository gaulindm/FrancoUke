// Draws every ABC notation block ({start_of_abc}...{end_of_abc}) with abcjs:
// treble-clef notation, plus a ukulele tab (standard GCEA, high G) under each staff.
// Add a line "%%notab" inside an ABC block to hide the tab for that block.
(function () {
  var SCALE = 1.5;                       // size of the notation (1.5 = 150%)
  var MAX_FRET = 12;                     // highest fret the tab will use
  var USE_G_STRING = false;              // false = melodies avoid the high G string (G4 is played as E-string fret 3)
  var OPEN = [67, 60, 64, 69];           // MIDI pitch of open strings: G4, C4, E4, A4
  var ROW = { 3: 0, 2: 1, 1: 2, 0: 3 }; // tab lines, top to bottom: A, E, C, G
  var NS = 'http://www.w3.org/2000/svg';

  // For the notes sounding together, pick a string + fret for each (lowest fret wins).
  function assignFrets(pitches) {
    var used = {}, out = [];
    pitches.slice().sort(function (a, b) { return b - a; }).forEach(function (p) {
      var best = null;
      for (var s = 0; s < 4; s++) {
        if (used[s] || (s === 0 && !USE_G_STRING)) continue;
        var fret = p - OPEN[s];
        if (fret >= 0 && fret <= MAX_FRET && (best === null || fret < best.fret)) best = { s: s, fret: fret };
      }
      if (best) { used[best.s] = true; out.push({ row: ROW[best.s], text: String(best.fret) }); }
      else {  // out of the ukulele's range: show "?" on a free line
        for (var r = 0; r < 4; r++) {
          var s2 = 3 - r;
          if (!used[s2] && (s2 !== 0 || USE_G_STRING)) { used[s2] = true; out.push({ row: r, text: '?' }); break; }
        }
      }
    });
    return out;
  }

  function el(name, attrs) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  function drawTab(tune, paper) {
    var svg = paper.querySelector('svg');
    if (!svg) return;
    try { ABCJS.synth.getMidiFile(tune, { midiOutputType: 'binary' }); } catch (e) { return; }
    var events = tune.setTiming(60, 0).filter(function (e) { return e.type === 'event' && e.left !== null; });
    if (!events.length) return;

    var SP = 7.5 * SCALE;                     // space between tab lines
    var GAP = 6 * SCALE;                      // gap between staff and tab
    var TAB_H = GAP + 3 * SP + 3 * SCALE;     // vertical room used per staff line
    var vb = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    var lines = 0;
    events.forEach(function (e) { lines = Math.max(lines, e.line + 1); });

    // Make room: push each later staff line down, and grow the picture
    var kids = Array.prototype.slice.call(svg.children);
    for (var L = 1; L < lines; L++) {
      kids.forEach(function (k) {
        if ((' ' + (k.getAttribute('class') || '') + ' ').indexOf(' abcjs-l' + L + ' ') >= 0 ||
            (k.getAttribute('class') || '').split(/\s+/).indexOf('abcjs-l' + L) >= 0)
          k.setAttribute('transform', 'translate(0,' + (L * TAB_H) + ')');
      });
    }
    var newH = vb[3] + lines * TAB_H;
    svg.setAttribute('viewBox', vb[0] + ' ' + vb[1] + ' ' + vb[2] + ' ' + newH);
    paper.style.paddingBottom = (newH / vb[2] * 100) + '%';

    var tabTop = {};   // y of the top tab line, per staff line
    for (var l = 0; l < lines; l++) {
      var ev0 = events.filter(function (e) { return e.line === l; })[0];
      if (!ev0) continue;
      var y0 = ev0.top + ev0.height + GAP + l * TAB_H;
      tabTop[l] = y0;
      var topLine = svg.querySelector('.abcjs-staff.abcjs-l' + l + ' .abcjs-top-line');
      var bb = topLine ? topLine.getBBox() : { x: 10, width: vb[2] - 20 };
      var x1 = bb.x, x2 = bb.x + bb.width;
      var g = el('g', { class: 'uke-tab' });
      for (var r = 0; r < 4; r++)
        g.appendChild(el('line', { x1: x1, x2: x2, y1: y0 + r * SP, y2: y0 + r * SP, 'stroke-width': 0.8, stroke: 'currentColor' }));
      // vertical start/end lines
      g.appendChild(el('line', { x1: x1, x2: x1, y1: y0, y2: y0 + 3 * SP, 'stroke-width': 1, stroke: 'currentColor' }));
      g.appendChild(el('line', { x1: x2, x2: x2, y1: y0, y2: y0 + 3 * SP, 'stroke-width': 1, stroke: 'currentColor' }));
      // "TAB" letters
      ['T', 'A', 'B'].forEach(function (ch, i) {
        // one letter in each of the three spaces between the four tab lines
        var t = el('text', { x: x1 + 14 * SCALE, y: y0 + (i + 0.5) * SP + 7 * SCALE * 0.36, 'text-anchor': 'middle',
                             'font-size': 7 * SCALE, 'font-weight': 'bold', 'font-family': 'sans-serif', fill: 'currentColor', stroke: 'none' });
        t.textContent = ch; g.appendChild(t);
      });
      svg.appendChild(g);
    }

    // Fret numbers
    var fs = 8.5 * SCALE;
    events.forEach(function (e) {
      if (tabTop[e.line] === undefined) return;
      var pitches = (e.midiPitches || []).map(function (m) { return m.pitch; });
      if (!pitches.length) return;
      var cx = e.left + (e.width || 0) / 2;
      assignFrets(pitches).forEach(function (n) {
        var t = el('text', { class: 'uke-fret', x: cx, y: tabTop[e.line] + n.row * SP + fs * 0.35, 'text-anchor': 'middle',
                             'font-size': fs, 'font-family': 'sans-serif', 'font-weight': 'bold',
                             fill: '#000', stroke: '#fff', 'stroke-width': fs * 0.5, 'paint-order': 'stroke' });
        t.textContent = n.text;
        svg.appendChild(t);
      });
    });
  }

  // Melody blocks stay hidden until the user turns them on (remembered on this device).
  var KEY = 'tpAbcVisible';          // '1' = show, anything else = hide
  var root = document.documentElement;
  // Is the teleprompter page dark right now? (Looks at the real page colours, so it
  // follows the Light/Dark buttons whatever the page does internally to switch.)
  function rgbOf(c) {
    var m = /rgba?\(([^)]+)\)/.exec(c || '');
    if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).map(parseFloat);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 && !isNaN(p[3]) ? p[3] : 1 };
  }
  function lum(c) { return (0.299 * c.r + 0.587 * c.g + 0.114 * c.b) / 255; }
  function pageIsDark() {
    var el = document.querySelector('.lyrics-container') || document.body;
    while (el) {
      var c = rgbOf(getComputedStyle(el).backgroundColor);
      if (c && c.a > 0.05) return lum(c) < 0.5;
      el = el.parentElement;
    }
    var t = rgbOf(getComputedStyle(document.body).color);   // no background found: judge by text colour
    return !!t && lum(t) > 0.5;
  }
  function syncTheme() { root.classList.toggle('abc-dark', pageIsDark()); }

  function savedVisible() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }

  document.addEventListener('DOMContentLoaded', function () {
    if (!window.ABCJS) return;
    var blocks = document.querySelectorAll('.abc-block');
    if (!blocks.length) return;               // no melody on this page: nothing to show, no button
    root.classList.remove('abc-off');          // draw while visible (the tab needs real sizes)...
    blocks.forEach(function (block) {
      var abc = block.dataset.abc || '';
      var paper = block.querySelector('.abc-paper');
      var wantTab = !/^%%notab\s*$/m.test(abc);
      if (!/^X:/m.test(abc)) abc = 'X:1\n' + abc;   // X: is required by ABC
      var tunes = ABCJS.renderAbc(paper, abc, { responsive: 'resize', add_classes: true, scale: SCALE });
      if (wantTab && tunes && tunes[0]) {
        try { drawTab(tunes[0], paper); } catch (err) { if (window.console) console.warn('Uke tab failed:', err); }
      }
    });

    // ...then apply the user's choice and wire up the 🎼 button (only present on pages with melody)
    var btn = document.getElementById('abc-toggle');
    function setVisible(show, save) {
      root.classList.toggle('abc-off', !show);
      if (btn) {
        btn.setAttribute('aria-pressed', show ? 'true' : 'false');
        btn.title = show ? 'Hide the melody notation' : 'Show the melody notation';
      }
      if (save) { try { localStorage.setItem(KEY, show ? '1' : '0'); } catch (e) {} }
    }
    if (btn) {
      btn.hidden = false;
      btn.addEventListener('click', function () { setVisible(root.classList.contains('abc-off'), true); });
    }
    setVisible(savedVisible(), false);

    syncTheme();
    if (window.MutationObserver) {
      var mo = new MutationObserver(syncTheme);
      [document.documentElement, document.body].forEach(function (n) {
        mo.observe(n, { attributes: true, attributeFilter: ['class', 'style', 'data-theme', 'data-bs-theme'] });
      });
    }
    ['theme-light', 'theme-dark'].forEach(function (id) {   // the Light/Dark buttons
      var b = document.getElementById(id);
      if (b) b.addEventListener('click', function () { setTimeout(syncTheme, 0); setTimeout(syncTheme, 150); });
    });
  });
})();