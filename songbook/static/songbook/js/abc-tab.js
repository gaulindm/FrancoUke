// Tablature for an abcjs drawing, for the member's own instrument.
// Draws a tab (4 to 6 lines, depending on the instrument) under each staff, with the fret
// numbers under their notes. Shared by the teleprompter (abc-blocks.js) and the Riff Lab page
// (riff-lab.js). Needs abcjs loaded first.
//
// Which instrument? An element anywhere on the page with data-tab-instrument="ukulele"
// (the page template fills it from the member's preferences); ukulele when there is none.
// Usage: AbcTab.draw(tuneObject, paperElement, scale)
(function () {
  var SCALE = 1.5;                       // default size of the notation (1.5 = 150%)
  var NS = 'http://www.w3.org/2000/svg';

  // ---- Instruments ---------------------------------------------------------------------------
  // strings: listed TOP LINE FIRST, as they appear in a tab. open = MIDI pitch of the open string
  // (60 = middle C).
  // fifth = banjo 5th string: it starts at the 5th fret, so its frets are numbered 6, 7, 8...
  // clef = for instruments whose music is written an octave above how it sounds (guitar): the melody is drawn
  // with the treble-8 clef, which also lowers the sound and the tab by an octave. Leave out when written at pitch.
  var TUNINGS = {
    ukulele:          { name: 'Ukulele',          maxFret: 12, strings: [{ open: 69 }, { open: 64 }, { open: 60 }, { open: 67 }] },   // A E C G (high G)
    baritone_ukulele: { name: 'Baritone Ukulele', maxFret: 12, strings: [{ open: 64 }, { open: 59 }, { open: 55 }, { open: 50 }] },                  // E B G D
    guitar:           { name: 'Guitar',           maxFret: 15, clef: 'treble-8', strings: [{ open: 64 }, { open: 59 }, { open: 55 }, { open: 50 }, { open: 45 }, { open: 40 }] },   // E B G D A E
    guitalele:        { name: 'Guitalele',        maxFret: 15, strings: [{ open: 69 }, { open: 64 }, { open: 60 }, { open: 55 }, { open: 50 }, { open: 45 }] },   // A E C G D A
    banjo:            { name: 'Banjo',            maxFret: 12, strings: [{ open: 62 }, { open: 59 }, { open: 55 }, { open: 50 }, { open: 67, fifth: true }] },   // D B G D, then the short g
    mandolin:         { name: 'Mandolin',         maxFret: 12, strings: [{ open: 76 }, { open: 69 }, { open: 62 }, { open: 55 }] }                   // E A D G
  };

  // Where is the member's instrument? Looked up in this order:
  //  1. the teleprompter's own settings block (#teleprompter-config), the same one the chord diagrams use
  //  2. data-tab-instrument="..." on any element (the Riff Lab page and the template fill this in)
  //  3. ukulele
  var lastSource = 'default';
  function instrumentKey() {
    var raw = '';
    try {
      var cfg = document.getElementById('teleprompter-config');
      var prefs = cfg ? (JSON.parse(cfg.textContent) || {}).userPreferences : null;
      if (prefs && prefs.instrument) { raw = prefs.instrument; lastSource = 'teleprompter-config'; }
    } catch (e) {}
    if (!raw && window.userPreferences && window.userPreferences.instrument) { raw = window.userPreferences.instrument; lastSource = 'window.userPreferences'; }
    if (!raw) {
      var node = document.querySelector('[data-tab-instrument]');
      if (node && node.getAttribute('data-tab-instrument')) { raw = node.getAttribute('data-tab-instrument'); lastSource = 'data-tab-instrument'; }
    }
    var key = String(raw || '').toLowerCase().replace(/[\s-]+/g, '_');   // "Baritone Ukulele" -> baritone_ukulele
    if (!TUNINGS[key]) { lastSource = 'default (unknown "' + raw + '")'; key = 'ukulele'; }
    return key;
  }

  function currentTuning() { return TUNINGS[instrumentKey()]; }

  // Adjusts the riff's ABC text for the member's instrument (adds clef=treble-8 for guitar).
  function prepare(abc) {
    var tn = currentTuning();
    if (!tn.clef) return abc;
    return abc.replace(/^(K:[^\n]*)$/m, function (line) {
      return /clef\s*=/.test(line) ? line : line.replace(/\s+$/, '') + ' clef=' + tn.clef;
    });
  }

  // The fret number that sounds pitch p on string s, or -1 if it can't.
  function fretOn(tn, s, p) {
    var str = tn.strings[s], d = p - str.open;
    if (d < 0) return -1;
    if (str.fifth && d > 0) d += 5;                       // 5th string: numbering starts at 6
    return d <= tn.maxFret ? d : -1;
  }

  // For the notes sounding together, pick a string + fret for each (lowest fret wins).
  function assignFrets(pitches, tn) {
    var used = {}, out = [];
    pitches.slice().sort(function (a, b) { return b - a; }).forEach(function (p) {
      var best = null;
      for (var s = 0; s < tn.strings.length; s++) {
        if (used[s]) continue;
        var f = fretOn(tn, s, p);
        if (f > 0 && tn.strings[s].fifth) f = f + 6;       // fretted banjo 5th string: last resort
        if (f >= 0 && (best === null || f < best.f)) best = { s: s, f: f };
      }
      if (best) { used[best.s] = true; out.push({ row: best.s, text: String(best.f > 0 && tn.strings[best.s].fifth ? best.f - 6 : best.f) }); }
      else {  // out of the instrument's range: show "?" on a free line
        for (var r = 0; r < tn.strings.length; r++) {
          if (!used[r]) { used[r] = true; out.push({ row: r, text: '?' }); break; }
        }
      }
    });
    return out;
  }

  // Notes played together (a chord): try every way of giving each note its own string
  // and keep the lowest, most compact frets.
  function assignChord(pitches, tn) {
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
      for (var s = 0; s < tn.strings.length; s++) {
        if (used[s]) continue;
        var f = fretOn(tn, s, ps[i]);
        if (f < 0) continue;
        used[s] = true; acc.push({ s: s, f: f });
        rec(i + 1, used, acc, cost + f + Math.max(0, f - 7) * 1.5);   // high frets are awkward in a chord
        acc.pop(); used[s] = false;
      }
    })(0, {}, [], 0);
    return best ? best.a.map(function (a) { return { row: a.s, text: String(a.f) }; }) : null;
  }

  function placeTogether(pitches, tn) {  // one note: simple rule; several: the chord search
    return (pitches.length > 1 && assignChord(pitches, tn)) || assignFrets(pitches, tn);
  }

  // ---- Easy hand position --------------------------------------------------------------------
  // Instead of choosing each note's lowest fret on its own, plan the whole melody at once:
  // stay near the hand's current fret, prefer open strings and low frets, avoid needless
  // string changes. (Dynamic programming over the notes, so it is the best overall path.)
  var EASY_HAND = true;                 // false = lowest fret for every note on its own
  var W_FRET = 1.0;                     // cost of fretting a note at all (open strings are easier)
  var W_LOW = 0.3;                      // plus this per fret number (low frets are easier)
  var W_HIGH = 0.5;                     // plus this per fret above the 9th
  var W_MOVE = 0.3;                     // cost per fret the hand has to travel
  var W_FAR = 0.15;                     // extra cost per fret beyond a 4-fret reach
  var W_STRING = 0.3;                   // cost of changing string

  function candidatesFor(p, tn) {       // every string/fret that can sound pitch p (in a melody)
    var out = [];
    for (var s = 0; s < tn.strings.length; s++) {
      var f = fretOn(tn, s, p);
      if (f >= 0 && !(tn.strings[s].fifth && f > 0)) out.push({ s: s, f: f });   // banjo 5th string: open only, in melodies
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
  function planFrets(events, tn) {
    tn = tn || currentTuning();
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
      seq.forEach(function (it) { plan[it.key] = placeTogether(it.pitches, tn); });
      return plan;
    }

    // states: { cost, s (last string, -1 none), hand (last fretted fret, 0 none), prev, place }
    var states = [{ cost: 0, s: -1, hand: 0, prev: null, place: null }];
    seq.forEach(function (it) {
      var next = {}, cands = it.pitches.length === 1 ? candidatesFor(it.pitches[0], tn) : [];
      var best = states.reduce(function (a, b) { return b.cost < a.cost ? b : a; });
      if (!cands.length) {              // chords and out-of-range notes: use the simple rule, keep the hand where it was
        var placed = placeTogether(it.pitches, tn);
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
              next[k] = { cost: cost, s: c.s, hand: hand, prev: st, place: [{ row: c.s, text: String(c.f) }] };
          });
        });
      }
      states = Object.keys(next).map(function (k) { return next[k]; });
    });

    var node = states.reduce(function (a, b) { return b.cost < a.cost ? b : a; });
    for (var i = seq.length - 1; i >= 0 && node; i--, node = node.prev) plan[seq[i].key] = node.place;
    return plan;
  }

  // ---- Drawing -------------------------------------------------------------------------------
  function el(name, attrs) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  function drawTab(tune, paper, scale) {
    var SC = scale || SCALE;
    var tn = currentTuning();
    var N = tn.strings.length;             // number of tab lines
    var svg = paper.querySelector('svg');
    if (!svg) return;
    try { ABCJS.synth.getMidiFile(tune, { midiOutputType: 'binary' }); } catch (e) { return; }
    var events = tune.setTiming(60, 0).filter(function (e) { return e.type === 'event' && e.left !== null; });
    if (!events.length) return;

    var SP = 7.5 * SC;                     // space between tab lines
    var GAP = 6 * SC;                      // gap between staff and tab
    var TAB_H = GAP + (N - 1) * SP + 3 * SC;   // vertical room used per staff line
    var vb = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    var lines = 0;
    events.forEach(function (e) { lines = Math.max(lines, e.line + 1); });

    // Make room: push each later staff line down, and grow the picture
    var kids = Array.prototype.slice.call(svg.children);
    for (var L = 1; L < lines; L++) {
      kids.forEach(function (k) {
        if ((k.getAttribute('class') || '').split(/\s+/).indexOf('abcjs-l' + L) >= 0)
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
      var g = el('g', { class: 'uke-tab', 'data-instrument': tn.name, 'data-source': lastSource });
      for (var r = 0; r < N; r++)
        g.appendChild(el('line', { x1: x1, x2: x2, y1: y0 + r * SP, y2: y0 + r * SP, 'stroke-width': 0.8, stroke: 'currentColor' }));
      // vertical start/end lines
      g.appendChild(el('line', { x1: x1, x2: x1, y1: y0, y2: y0 + (N - 1) * SP, 'stroke-width': 1, stroke: 'currentColor' }));
      g.appendChild(el('line', { x1: x2, x2: x2, y1: y0, y2: y0 + (N - 1) * SP, 'stroke-width': 1, stroke: 'currentColor' }));
      // "TAB" letters: one in each of three spaces, in the middle of the lines
      var firstSpace = Math.floor((N - 1 - 3) / 2) + 0.5;
      ['T', 'A', 'B'].forEach(function (ch, i) {
        var t = el('text', { x: x1 + 14 * SC, y: y0 + (firstSpace + i) * SP + 7 * SC * 0.36, 'text-anchor': 'middle',
                             'font-size': 7 * SC, 'font-weight': 'bold', 'font-family': 'sans-serif', fill: 'currentColor', stroke: 'none' });
        t.textContent = ch; g.appendChild(t);
      });
      svg.appendChild(g);
    }

    // Fret numbers
    var fs = 8.5 * SC;
    var plan = planFrets(events, tn), drawn = {};
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

  window.AbcTab = { VERSION: 'multi-instrument 2026-11-09', draw: drawTab, prepare: prepare, SCALE: SCALE, TUNINGS: TUNINGS, instrumentKey: instrumentKey, planFrets: planFrets, assignFrets: assignFrets };
})();