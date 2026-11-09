// abc-blocks.js
// Multi-instrument ABC notation and tablature renderer.
//
// Instruments:
//   ukulele, baritone ukulele, guitar, guitalele, banjo, mandolin
//
// Features:
//   - ABCJS SVG generation
//   - Instrument-specific tablature
//   - Guitar treble-8 clef
//   - Easy-hand fret positioning
//   - Multiple ABC blocks per page
//   - %%notab support
//   - Remembered melody visibility
//   - Automatic light/dark theme detection
//
// Dependencies:
//   abcjs must be loaded before this script.
//
// Instrument selection:
//   1. #teleprompter-config userPreferences.instrument
//   2. window.userPreferences.instrument
//   3. [data-tab-instrument]
//   4. ukulele (default)

(function () {
  'use strict';

  // ===========================================================================
  // CONFIGURATION
  // ===========================================================================

  var SCALE = 1.5;
  var USE_G_STRING = false;
  var NS = 'http://www.w3.org/2000/svg';

  var KEY = 'tpAbcVisible';

  // ===========================================================================
  // INSTRUMENT DEFINITIONS
  // ===========================================================================

  // Strings are listed TOP LINE FIRST.
  // open = MIDI pitch of the open string.
  // avoid = excluded from single-note melodies.
  // fifth = banjo short fifth string.

  var TUNINGS = {
    ukulele: {
      name: 'Ukulele',
      maxFret: 12,
      strings: [
        { open: 69 },
        { open: 64 },
        { open: 60 },
        { open: 67, avoid: true }
      ]
    },

    baritone_ukulele: {
      name: 'Baritone Ukulele',
      maxFret: 12,
      strings: [
        { open: 64 },
        { open: 59 },
        { open: 55 },
        { open: 50 }
      ]
    },

    guitar: {
      name: 'Guitar',
      maxFret: 15,
      clef: 'treble-8',
      strings: [
        { open: 64 },
        { open: 59 },
        { open: 55 },
        { open: 50 },
        { open: 45 },
        { open: 40 }
      ]
    },

    guitalele: {
      name: 'Guitalele',
      maxFret: 15,
      strings: [
        { open: 69 },
        { open: 64 },
        { open: 60 },
        { open: 55 },
        { open: 50 },
        { open: 45 }
      ]
    },

    banjo: {
      name: 'Banjo',
      maxFret: 12,
      strings: [
        { open: 62 },
        { open: 59 },
        { open: 55 },
        { open: 50 },
        { open: 67, fifth: true }
      ]
    },

    mandolin: {
      name: 'Mandolin',
      maxFret: 12,
      strings: [
        { open: 76 },
        { open: 69 },
        { open: 62 },
        { open: 55 }
      ]
    }
  };

  // ===========================================================================
  // INSTRUMENT DETECTION
  // ===========================================================================

  var lastSource = 'default';

  function instrumentKey() {
    var raw = '';

    try {
      var cfg = document.getElementById('teleprompter-config');

      var prefs = cfg
        ? (JSON.parse(cfg.textContent) || {}).userPreferences
        : null;

      if (prefs && prefs.instrument) {
        raw = prefs.instrument;
        lastSource = 'teleprompter-config';
      }
    } catch (e) {
      // Continue to other preference sources.
    }

    if (
      !raw &&
      window.userPreferences &&
      window.userPreferences.instrument
    ) {
      raw = window.userPreferences.instrument;
      lastSource = 'window.userPreferences';
    }

    if (!raw) {
      var node = document.querySelector('[data-tab-instrument]');

      if (node && node.getAttribute('data-tab-instrument')) {
        raw = node.getAttribute('data-tab-instrument');
        lastSource = 'data-tab-instrument';
      }
    }

    var key = String(raw || '')
      .toLowerCase()
      .replace(/[\s-]+/g, '_');

    if (!TUNINGS[key]) {
      lastSource = 'default (unknown "' + raw + '")';
      key = 'ukulele';
    }

    return key;
  }

  function currentTuning() {
    return TUNINGS[instrumentKey()];
  }

  // ===========================================================================
  // PREPARE ABC FOR INSTRUMENT
  // ===========================================================================

  function prepare(abc) {
    var tn = currentTuning();

    if (!tn.clef) return abc;

    var foundKey = false;

    abc = abc.replace(/^(K:[^\r\n]*)$/m, function (line) {
      foundKey = true;

      if (/clef\s*=/.test(line)) return line;

      return line.replace(/\s+$/, '') +
        ' clef=' + tn.clef;
    });

    // If there is no K: line, provide a default key/clef.
    if (!foundKey) {
      abc = abc.replace(
        /^(X:[^\r\n]*\r?\n)/m,
        '$1K:C clef=' + tn.clef + '\n'
      );
    }

    return abc;
  }

  // ===========================================================================
  // FRET CALCULATIONS
  // ===========================================================================

  function fretOn(tn, s, p) {
    var str = tn.strings[s];

    var d = p - str.open;

    if (d < 0) return -1;

    // Banjo fifth string starts fretting at physical fret 6.
    if (str.fifth && d > 0) d += 5;

    return d <= tn.maxFret ? d : -1;
  }

  // ---------------------------------------------------------------------------
  // Assign notes independently.
  // ---------------------------------------------------------------------------

  function assignFrets(pitches, tn) {
    var used = {};
    var out = [];

    pitches.slice().sort(function (a, b) {
      return b - a;
    }).forEach(function (p) {

      var best = null;

      for (var s = 0; s < tn.strings.length; s++) {
        if (
          used[s] ||
          (tn.strings[s].avoid && !USE_G_STRING)
        ) continue;

        var f = fretOn(tn, s, p);

        if (
          f >= 0 &&
          (best === null || f < best.f)
        ) {
          best = { s: s, f: f };
        }
      }

      if (best) {
        used[best.s] = true;

        out.push({
          row: best.s,
          text: String(best.f)
        });

      } else {
        // Out-of-range note.
        for (var r = 0; r < tn.strings.length; r++) {
          if (
            !used[r] &&
            (!tn.strings[r].avoid || USE_G_STRING)
          ) {
            used[r] = true;

            out.push({
              row: r,
              text: '?'
            });

            break;
          }
        }
      }
    });

    return out;
  }

  // ---------------------------------------------------------------------------
  // Assign simultaneous notes to different strings.
  // ---------------------------------------------------------------------------

  function assignChord(pitches, tn) {
    var ps = pitches.slice().sort(function (a, b) {
      return b - a;
    });

    var best = null;

    (function rec(i, used, acc, cost) {

      if (i === ps.length) {
        var fr = acc
          .filter(function (a) {
            return a.f > 0;
          })
          .map(function (a) {
            return a.f;
          });

        var span = fr.length
          ? Math.max.apply(null, fr) - Math.min.apply(null, fr)
          : 0;

        var c = cost + span * 0.5 +
          (span > 4 ? 100 : 0);

        if (!best || c < best.c) {
          best = {
            c: c,
            a: acc.slice()
          };
        }

        return;
      }

      for (var s = 0; s < tn.strings.length; s++) {
        if (used[s]) continue;

        var f = fretOn(tn, s, ps[i]);

        if (f < 0) continue;

        used[s] = true;

        acc.push({
          s: s,
          f: f
        });

        rec(
          i + 1,
          used,
          acc,
          cost + f + Math.max(0, f - 7) * 1.5
        );

        acc.pop();
        used[s] = false;
      }

    })(0, {}, [], 0);

    return best
      ? best.a.map(function (a) {
          return {
            row: a.s,
            text: String(a.f)
          };
        })
      : null;
  }

  function placeTogether(pitches, tn) {
    return (
      pitches.length > 1 &&
      assignChord(pitches, tn)
    ) || assignFrets(pitches, tn);
  }

  // ===========================================================================
  // EASY HAND POSITIONING
  // ===========================================================================

  var EASY_HAND = true;

  var W_FRET = 1.0;
  var W_LOW = 0.3;
  var W_HIGH = 0.5;
  var W_MOVE = 0.3;
  var W_FAR = 0.15;
  var W_STRING = 0.3;

  function candidatesFor(p, tn) {
    var out = [];

    for (var s = 0; s < tn.strings.length; s++) {
      if (tn.strings[s].avoid && !USE_G_STRING) continue;

      var f = fretOn(tn, s, p);

      if (
        f >= 0 &&
        !(tn.strings[s].fifth && f > 0)
      ) {
        out.push({
          s: s,
          f: f
        });
      }
    }

    return out;
  }

  function unaryCost(f) {
    return f === 0
      ? 0
      : W_FRET +
        f * W_LOW +
        Math.max(0, f - 9) * W_HIGH;
  }

  function moveCost(f, hand) {
    if (f === 0 || hand === 0) return 0;

    var d = Math.abs(f - hand);

    return d * W_MOVE +
      Math.max(0, d - 4) * W_FAR;
  }

  // ---------------------------------------------------------------------------
  // Plan the whole melody.
  // ---------------------------------------------------------------------------

  function planFrets(events, tn) {
    tn = tn || currentTuning();

    var seen = {};
    var seq = [];

    events.forEach(function (e) {
      var key = e.line + ':' + e.left;

      if (seen[key]) return;

      seen[key] = true;

      var pitches = (e.midiPitches || []).map(function (m) {
        return m.pitch;
      });

      if (pitches.length) {
        seq.push({
          key: key,
          pitches: pitches
        });
      }
    });

    var plan = {};

    if (!EASY_HAND) {
      seq.forEach(function (it) {
        plan[it.key] = placeTogether(it.pitches, tn);
      });

      return plan;
    }

    var states = [{
      cost: 0,
      s: -1,
      hand: 0,
      prev: null,
      place: null
    }];

    seq.forEach(function (it) {

      var next = {};

      var cands = it.pitches.length === 1
        ? candidatesFor(it.pitches[0], tn)
        : [];

      var best = states.reduce(function (a, b) {
        return b.cost < a.cost ? b : a;
      });

      if (!cands.length) {

        // Chords and out-of-range notes.
        var placed = placeTogether(it.pitches, tn);

        var hand = best.hand;

        placed.forEach(function (n) {
          if (
            n.text !== '?' &&
            parseInt(n.text, 10) > 0
          ) {
            hand = parseInt(n.text, 10);
          }
        });

        next.fixed = {
          cost: best.cost,
          s: -1,
          hand: hand,
          prev: best,
          place: placed
        };

      } else {

        cands.forEach(function (c) {

          states.forEach(function (st) {

            var cost = st.cost +
              unaryCost(c.f) +
              moveCost(c.f, st.hand) +
              (
                st.s !== -1 && st.s !== c.s
                  ? W_STRING
                  : 0
              );

            var hand = c.f > 0
              ? c.f
              : st.hand;

            var k = c.s + '|' + c.f + '|' + hand;

            if (!next[k] || cost < next[k].cost) {
              next[k] = {
                cost: cost,
                s: c.s,
                hand: hand,
                prev: st,
                place: [{
                  row: c.s,
                  text: String(c.f)
                }]
              };
            }
          });
        });
      }

      states = Object.keys(next).map(function (k) {
        return next[k];
      });
    });

    if (!seq.length || !states.length) return plan;

    var node = states.reduce(function (a, b) {
      return b.cost < a.cost ? b : a;
    });

    for (
      var i = seq.length - 1;
      i >= 0 && node;
      i--, node = node.prev
    ) {
      plan[seq[i].key] = node.place;
    }

    return plan;
  }

  // ===========================================================================
  // SVG DRAWING HELPERS
  // ===========================================================================

  function el(name, attrs) {
    var e = document.createElementNS(NS, name);

    for (var k in attrs) {
      e.setAttribute(k, attrs[k]);
    }

    return e;
  }

  // ===========================================================================
  // DRAW MULTI-INSTRUMENT TAB
  // ===========================================================================

  function drawTab(tune, paper, scale) {
    var SC = scale || SCALE;

    var tn = currentTuning();

    var N = tn.strings.length;

    var svg = paper.querySelector('svg');

    if (!svg) return;

    // Verify ABCJS generated usable MIDI information.
    try {
      ABCJS.synth.getMidiFile(tune, {
        midiOutputType: 'binary'
      });
    } catch (e) {
      if (window.console) {
        console.warn('ABC tab MIDI preparation failed:', e);
      }
      return;
    }

    var events = tune.setTiming(60, 0).filter(function (e) {
      return e.type === 'event' && e.left !== null;
    });

    if (!events.length) return;

    var SP = 7.5 * SC;
    var GAP = 6 * SC;

    var TAB_H = GAP +
      (N - 1) * SP +
      3 * SC;

    var viewBox = svg.getAttribute('viewBox');

    if (!viewBox) {
      console.warn('ABC SVG has no viewBox.');
      return;
    }

    var vb = viewBox.trim().split(/\s+/).map(Number);

    if (vb.length !== 4 || !isFinite(vb[2]) || vb[2] <= 0) {
      console.warn('Invalid ABC SVG viewBox:', viewBox);
      return;
    }

    var lines = 0;

    events.forEach(function (e) {
      lines = Math.max(lines, e.line + 1);
    });

    // -----------------------------------------------------------------------
    // Make room below each staff.
    // -----------------------------------------------------------------------

    var kids = Array.prototype.slice.call(svg.children);

    for (var L = 1; L < lines; L++) {

      kids.forEach(function (k) {

        var classes = (k.getAttribute('class') || '')
          .split(/\s+/);

        if (classes.indexOf('abcjs-l' + L) >= 0) {
          k.setAttribute(
            'transform',
            'translate(0,' + (L * TAB_H) + ')'
          );
        }
      });
    }

    var newH = vb[3] + lines * TAB_H;

    svg.setAttribute(
      'viewBox',
      vb[0] + ' ' +
      vb[1] + ' ' +
      vb[2] + ' ' +
      newH
    );

    paper.style.paddingBottom =
      (newH / vb[2] * 100) + '%';

    // -----------------------------------------------------------------------
    // Draw the tab lines for each staff.
    // -----------------------------------------------------------------------

    var tabTop = {};

    for (var l = 0; l < lines; l++) {

      var ev0 = events.filter(function (e) {
        return e.line === l;
      })[0];

      if (!ev0) continue;

      var y0 = ev0.top +
        ev0.height +
        GAP +
        l * TAB_H;

      tabTop[l] = y0;

      var topLine = svg.querySelector(
        '.abcjs-staff.abcjs-l' + l + ' .abcjs-top-line'
      );

      var bb = topLine
        ? topLine.getBBox()
        : {
            x: 10,
            width: vb[2] - 20
          };

      var x1 = bb.x;
      var x2 = bb.x + bb.width;

      var g = el('g', {
        class: 'uke-tab',
        'data-instrument': tn.name,
        'data-source': lastSource
      });

      // Horizontal strings.
      for (var r = 0; r < N; r++) {
        g.appendChild(el('line', {
          x1: x1,
          x2: x2,
          y1: y0 + r * SP,
          y2: y0 + r * SP,
          'stroke-width': 0.8,
          stroke: 'currentColor'
        }));
      }

      // Vertical boundaries.
      g.appendChild(el('line', {
        x1: x1,
        x2: x1,
        y1: y0,
        y2: y0 + (N - 1) * SP,
        'stroke-width': 1,
        stroke: 'currentColor'
      }));

      g.appendChild(el('line', {
        x1: x2,
        x2: x2,
        y1: y0,
        y2: y0 + (N - 1) * SP,
        'stroke-width': 1,
        stroke: 'currentColor'
      }));

      // TAB letters positioned in three available spaces.
      var firstSpace = Math.floor((N - 1 - 3) / 2) + 0.5;

      ['T', 'A', 'B'].forEach(function (ch, i) {

        var t = el('text', {
          x: x1 + 14 * SC,
          y: y0 +
            (firstSpace + i) * SP +
            7 * SC * 0.36,
          'text-anchor': 'middle',
          'font-size': 7 * SC,
          'font-weight': 'bold',
          'font-family': 'sans-serif',
          fill: 'currentColor',
          stroke: 'none'
        });

        t.textContent = ch;

        g.appendChild(t);
      });

      svg.appendChild(g);
    }

    // -----------------------------------------------------------------------
    // Draw fret numbers.
    // -----------------------------------------------------------------------

    var fs = 8.5 * SC;

    var plan = planFrets(events, tn);

    var drawn = {};

    events.forEach(function (e) {

      var key = e.line + ':' + e.left;

      if (
        tabTop[e.line] === undefined ||
        drawn[key] ||
        !plan[key]
      ) return;

      drawn[key] = true;

      var cx = e.left + (e.width || 0) / 2;

      plan[key].forEach(function (n) {

        var t = el('text', {
          class: 'uke-fret',
          x: cx,
          y: tabTop[e.line] + n.row * SP + fs * 0.35,
          'text-anchor': 'middle',
          'font-size': fs,
          'font-family': 'sans-serif',
          'font-weight': 'bold',
          fill: '#000',
          stroke: '#fff',
          'stroke-width': fs * 0.5,
          'paint-order': 'stroke'
        });

        t.textContent = n.text;

        svg.appendChild(t);
      });
    });
  }

  // ===========================================================================
  // PUBLIC TAB API
  // ===========================================================================

  window.AbcTab = {
    VERSION: 'multi-instrument-integrated-2026-11-09',
    draw: drawTab,
    prepare: prepare,
    SCALE: SCALE,
    TUNINGS: TUNINGS,
    instrumentKey: instrumentKey,
    planFrets: planFrets,
    assignFrets: assignFrets
  };

  // ===========================================================================
  // THEME DETECTION
  // ===========================================================================

  var root = document.documentElement;

  function rgbOf(c) {
    var m = /rgba?\(([^)]+)\)/.exec(c || '');

    if (!m) return null;

    var p = m[1].split(/[ ,\/]+/).map(parseFloat);

    return {
      r: p[0],
      g: p[1],
      b: p[2],
      a: p.length > 3 && !isNaN(p[3]) ? p[3] : 1
    };
  }

  function lum(c) {
    return (
      0.299 * c.r +
      0.587 * c.g +
      0.114 * c.b
    ) / 255;
  }

  function pageIsDark() {

    var node =
      document.querySelector('.lyrics-container') ||
      document.body;

    while (node) {

      var c = rgbOf(
        getComputedStyle(node).backgroundColor
      );

      if (c && c.a > 0.05) {
        return lum(c) < 0.5;
      }

      node = node.parentElement;
    }

    var t = rgbOf(
      getComputedStyle(document.body).color
    );

    return !!t && lum(t) > 0.5;
  }

  function syncTheme() {
    root.classList.toggle(
      'abc-dark',
      pageIsDark()
    );
  }

  // ===========================================================================
  // VISIBILITY PREFERENCE
  // ===========================================================================

  function savedVisible() {
    try {
      return localStorage.getItem(KEY) === '1';
    } catch (e) {
      return false;
    }
  }

  function setVisible(show, save, btn) {

    root.classList.toggle('abc-off', !show);

    if (btn) {

      btn.setAttribute(
        'aria-pressed',
        show ? 'true' : 'false'
      );

      btn.title = show
        ? 'Hide the melody notation'
        : 'Show the melody notation';
    }

    if (save) {
      try {
        localStorage.setItem(
          KEY,
          show ? '1' : '0'
        );
      } catch (e) {
        // Storage may be disabled.
      }
    }
  }

  // ===========================================================================
  // ABC BLOCK RENDERING
  // ===========================================================================

  function renderBlocks() {

    if (!window.ABCJS) {
      console.error(
        'abc-blocks.js: ABCJS is not loaded.'
      );
      return;
    }

    var blocks = document.querySelectorAll('.abc-block');

    if (!blocks.length) return;

    // Draw while visible so SVG measurements and getBBox() work.
    root.classList.remove('abc-off');

    blocks.forEach(function (block) {

      var abc = block.dataset.abc || '';

      var paper = block.querySelector('.abc-paper');

      if (!paper) {
        console.warn(
          'ABC block has no .abc-paper element.',
          block
        );
        return;
      }

      // Detect and remove the custom no-tab directive.
      var wantTab = !/^%%notab\s*$/m.test(abc);

      abc = abc.replace(
        /^\s*%%notab\s*$(?:\r?\n)?/gm,
        ''
      );

      // ABC requires an X: reference.
      if (!/^X:/m.test(abc)) {
        abc = 'X:1\n' + abc;
      }

      // Prepare the notation for the selected instrument.
      abc = prepare(abc);

      try {

        // ---------------------------------------------------------------
        // THIS IS THE SVG GENERATION STEP.
        // ---------------------------------------------------------------

        var tunes = ABCJS.renderAbc(
          paper,
          abc,
          {
            responsive: 'resize',
            add_classes: true,
            scale: SCALE
          }
        );

        // ---------------------------------------------------------------
        // Draw the selected instrument's tablature.
        // ---------------------------------------------------------------

        if (
          wantTab &&
          tunes &&
          tunes[0]
        ) {
          drawTab(
            tunes[0],
            paper,
            SCALE
          );
        }

      } catch (err) {

        console.error(
          'ABC rendering failed:',
          err,
          block
        );
      }
    });

    // =========================================================================
    // MELODY VISIBILITY BUTTON
    // =========================================================================

    var btn = document.getElementById('abc-toggle');

    if (btn) {

      btn.hidden = false;

      btn.addEventListener('click', function () {

        var show = root.classList.contains('abc-off');

        setVisible(show, true, btn);
      });
    }

    setVisible(
      savedVisible(),
      false,
      btn
    );

    // =========================================================================
    // THEME SYNCHRONIZATION
    // =========================================================================

    syncTheme();

    if (window.MutationObserver) {

      var mo = new MutationObserver(function () {
        syncTheme();
      });

      [document.documentElement, document.body].forEach(
        function (node) {

          if (!node) return;

          mo.observe(node, {
            attributes: true,
            attributeFilter: [
              'class',
              'style',
              'data-theme',
              'data-bs-theme'
            ]
          });
        }
      );
    }

    // Light/dark theme buttons.
    ['theme-light', 'theme-dark'].forEach(function (id) {

      var b = document.getElementById(id);

      if (b) {

        b.addEventListener('click', function () {

          setTimeout(syncTheme, 0);
          setTimeout(syncTheme, 150);
        });
      }
    });
  }

  // ===========================================================================
  // INITIALIZATION
  // ===========================================================================

  var initialized = false;

  function init() {

    if (initialized) return;

    initialized = true;

    renderBlocks();
  }

  // Works whether the script loads before or after DOMContentLoaded.
  if (document.readyState === 'loading') {

    document.addEventListener(
      'DOMContentLoaded',
      init,
      { once: true }
    );

  } else {

    init();
  }

})();