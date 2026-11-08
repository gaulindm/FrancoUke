// Ukulele tab for an abcjs drawing: draws a 4-line tab (standard GCEA, high G) under each
// staff, with the fret numbers under their notes. Shared by the teleprompter (abc-blocks.js)
// and the Riff Lab page (riff-lab.js). Needs abcjs loaded first.
// Usage: AbcTab.draw(tuneObject, paperElement, scale)
(function () {
    var SCALE = 1.5;                       // default size of the notation (1.5 = 150%)
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
  
    // Notes played together (a chord): try every way of giving each note its own string
    // (the high G string IS allowed here) and keep the one with the lowest, most compact frets.
    function assignChord(pitches) {
      var ps = pitches.slice().sort(function (a, b) { return b - a; });
      var best = null;
      (function rec(i, used, acc, cost) {
        if (i === ps.length) {
          var fr = acc.filter(function (a) { return a.f > 0; }).map(function (a) { return a.f; });
          var span = fr.length ? Math.max.apply(null, fr) - Math.min.apply(null, fr) : 0;
          var c = cost + span * 0.5 + (span > 4 ? 100 : 0);
          if (!best || c < best.c) best = { c: c, a: acc.slice() };
          return;
        }
        for (var s = 0; s < 4; s++) {
          if (used[s]) continue;
          var f = ps[i] - OPEN[s];
          if (f < 0 || f > MAX_FRET) continue;
          used[s] = true; acc.push({ s: s, f: f });
          rec(i + 1, used, acc, cost + f);
          acc.pop(); used[s] = false;
        }
      })(0, {}, [], 0);
      return best ? best.a.map(function (a) { return { row: ROW[a.s], text: String(a.f) }; }) : null;
    }
  
    function placeTogether(pitches) {      // one note: simple rule; several: the chord search
      return (pitches.length > 1 && assignChord(pitches)) || assignFrets(pitches);
    }
  
    // ---- Easy hand position -------------------------------------------------------------------
    // Instead of choosing each note's lowest fret on its own, plan the whole melody at once:
    // stay near the hand's current fret, prefer open strings and low frets, avoid needless
    // string changes. (Dynamic programming over the notes, so it is the best overall path.)
    var EASY_HAND = true;                 // false = old behaviour: lowest fret for every note on its own
    var W_FRET = 0.8;                     // cost of fretting a note at all (open strings are easier)
    var W_LOW = 0.2;                      // plus this per fret number (low frets are easier)
    var W_HIGH = 0.5;                     // plus this per fret above the 9th
    var W_MOVE = 0.3;                     // cost per fret the hand has to travel
    var W_FAR = 0.5;                      // extra cost per fret beyond a 4-fret reach
    var W_STRING = 0.3;                   // cost of changing string
  
    function candidatesFor(p) {           // every string/fret that can sound pitch p
      var out = [];
      for (var s = 0; s < 4; s++) {
        if (s === 0 && !USE_G_STRING) continue;
        var f = p - OPEN[s];
        if (f >= 0 && f <= MAX_FRET) out.push({ s: s, f: f });
      }
      return out;
    }
  
    function unaryCost(f) { return f === 0 ? 0 : W_FRET + f * W_LOW + Math.max(0, f - 9) * W_HIGH; }
  
    function moveCost(f, hand) {          // cost of fretting f when the hand is at 'hand' (0 = no fretted note yet)
      if (f === 0 || hand === 0) return 0;          // open strings don't move the hand
      var d = Math.abs(f - hand);
      return d * W_MOVE + Math.max(0, d - 4) * W_FAR;
    }
  
    // events: timing events (in time order). Returns { "line:left": [ {row, text}, ... ] }
    function planFrets(events) {
      var seen = {}, seq = [];
      events.forEach(function (e) {       // one entry per printed note (repeats play the same notes again)
        var key = e.line + ':' + e.left;
        if (seen[key]) return;
        seen[key] = true;
        var pitches = (e.midiPitches || []).map(function (m) { return m.pitch; });
        if (pitches.length) seq.push({ key: key, pitches: pitches });
      });
  
      var plan = {};
      if (!EASY_HAND) {
        seq.forEach(function (it) { plan[it.key] = placeTogether(it.pitches); });
        return plan;
      }
  
      // states: { cost, s (last string, -1 none), hand (last fretted fret, 0 none), prev, place }
      var states = [{ cost: 0, s: -1, hand: 0, prev: null, place: null }];
      seq.forEach(function (it) {
        var next = {}, cands = it.pitches.length === 1 ? candidatesFor(it.pitches[0]) : [];
        var best = states.reduce(function (a, b) { return b.cost < a.cost ? b : a; });
        if (!cands.length) {              // chords and out-of-range notes: use the simple rule, keep the hand where it was
          var placed = placeTogether(it.pitches);
          var hand = best.hand;
          placed.forEach(function (n) { if (n.text !== '?' && parseInt(n.text, 10) > 0) hand = parseInt(n.text, 10); });
          next['fixed'] = { cost: best.cost, s: -1, hand: hand, prev: best, place: placed };
        } else {
          cands.forEach(function (c) {
            states.forEach(function (st) {
              var cost = st.cost + unaryCost(c.f) + moveCost(c.f, st.hand) + (st.s !== -1 && st.s !== c.s ? W_STRING : 0);
              var hand = c.f > 0 ? c.f : st.hand;
              var k = c.s + '|' + c.f + '|' + hand;
              if (!next[k] || cost < next[k].cost)
                next[k] = { cost: cost, s: c.s, hand: hand, prev: st, place: [{ row: ROW[c.s], text: String(c.f) }] };
            });
          });
        }
        states = Object.keys(next).map(function (k) { return next[k]; });
      });
  
      var node = states.reduce(function (a, b) { return b.cost < a.cost ? b : a; });
      for (var i = seq.length - 1; i >= 0 && node; i--, node = node.prev) plan[seq[i].key] = node.place;
      return plan;
    }
  
    function el(name, attrs) {
      var e = document.createElementNS(NS, name);
      for (var k in attrs) e.setAttribute(k, attrs[k]);
      return e;
    }
  
    function drawTab(tune, paper, scale) {
      var SC = scale || SCALE;
      var svg = paper.querySelector('svg');
      if (!svg) return;
      try { ABCJS.synth.getMidiFile(tune, { midiOutputType: 'binary' }); } catch (e) { return; }
      var events = tune.setTiming(60, 0).filter(function (e) { return e.type === 'event' && e.left !== null; });
      if (!events.length) return;
  
      var SP = 7.5 * SC;                     // space between tab lines
      var GAP = 6 * SC;                      // gap between staff and tab
      var TAB_H = GAP + 3 * SP + 3 * SC;     // vertical room used per staff line
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
          var t = el('text', { x: x1 + 14 * SC, y: y0 + (i + 0.5) * SP + 7 * SC * 0.36, 'text-anchor': 'middle',
                               'font-size': 7 * SC, 'font-weight': 'bold', 'font-family': 'sans-serif', fill: 'currentColor', stroke: 'none' });
          t.textContent = ch; g.appendChild(t);
        });
        svg.appendChild(g);
      }
  
      // Fret numbers
      var fs = 8.5 * SC;
      var plan = planFrets(events), drawn = {};
      events.forEach(function (e) {
        var key = e.line + ':' + e.left;
        if (tabTop[e.line] === undefined || drawn[key] || !plan[key]) return;
        drawn[key] = true;
        var cx = e.left + (e.width || 0) / 2;
        plan[key].forEach(function (n) {
          var t = el('text', { class: 'uke-fret', x: cx, y: tabTop[e.line] + n.row * SP + fs * 0.35, 'text-anchor': 'middle',
                               'font-size': fs, 'font-family': 'sans-serif', 'font-weight': 'bold',
                               fill: '#000', stroke: '#fff', 'stroke-width': fs * 0.5, 'paint-order': 'stroke' });
          t.textContent = n.text;
          svg.appendChild(t);
        });
      });
    }
  
    window.AbcTab = { draw: drawTab, SCALE: SCALE, planFrets: planFrets, assignFrets: assignFrets };
  })();