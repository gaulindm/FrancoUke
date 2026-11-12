(function () {
  var ctx = null, raf = 0, ticker = 0, live = [], overlay = null, parts = null, running = false;

  var NOTE_SECONDS = 2.2;   // 🔧 TUNE: how long the first note is held before the count starts
  var NOTE_INDEX = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  var NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

  // ---------- note helpers ----------
  function parseNote(note) {
    var m = /^([A-G])([#b]?)(\d)?$/.exec(note || "");
    if (!m) return null;
    var n = NOTE_INDEX[m[1]] + (m[2] === "#" ? 1 : m[2] === "b" ? -1 : 0);
    return { n: n, octave: m[3] ? parseInt(m[3], 10) : 4 };   // no octave written = octave 4
  }
  function midiOf(p, shift) { return 12 * (p.octave + 1) + p.n + (shift || 0); }
  function freqOf(midi) { return 440 * Math.pow(2, (midi - 69) / 12); }
  function nameOf(midi) { return NAMES[((midi % 12) + 12) % 12]; }

  // ---------- the timeline: one list drives both the sound and the screen ----------
  // 4/4:  note, then   "1, 2,  1 2 3 4"
  // 2/2:  note, then   "1, 2,  1 & 2 &"
  // 3/4, 6/8, 5/4 ...: two full bars, "1 2 3  1 2 3", strong beat (1) of each bar accented
  // After the count the ticks carry on (see startTicks) from the time in "end".
  function buildSequence(cue, shift) {
    var ev = [], t = 0, pips = [], meter = null;
    var p = parseNote(cue.note);
    if (p) {
      var midi = midiOf(p, shift);
      ev.push({ t: 0, kind: "note", main: nameOf(midi), sub: "your first note", freq: freqOf(midi) });
      t = NOTE_SECONDS;
    }
    if (cue.tempo) {
      var beat = 60 / cue.tempo;
      var cut = cue.time === "2/2";
      var common = !cue.time || cue.time === "4/4";
      var n = cue.beats || 4;
      meter = { beat: beat, n: cut ? 2 : n, cut: cut };

      if (!cut && !common) {
        // Two full bars. The first is the "get ready" bar (grey), the second is
        // the bar to join in on. Beat 1 of each bar is the strong beat.
        for (var bar = 0; bar < 2; bar++) {
          for (var k = 0; k < n; k++) {
            if (bar === 0) pips.push(String(k + 1));
            ev.push({
              t: t, kind: bar === 0 ? "lead" : "bar", main: String(k + 1),
              sub: bar === 0 ? "get ready" : "", pip: k, accent: k === 0
            });
            t += beat;
          }
        }
        return { events: ev, end: t, pips: pips, meter: meter };
      }

      ev.push({ t: t, kind: "lead", main: "1", sub: "get ready" }); t += beat;
      ev.push({ t: t, kind: "lead", main: "2", sub: "get ready" }); t += beat;

      if (cut) {
        pips = ["1", "&", "2", "&"];
        for (var b = 0; b < 2; b++) {
          ev.push({ t: t, kind: "bar", main: String(b + 1), pip: b * 2, accent: b === 0 });
          ev.push({ t: t + beat / 2, kind: "bar", main: "&", pip: b * 2 + 1, offbeat: true });
          t += beat;
        }
      } else {
        for (var i = 0; i < n; i++) {
          pips.push(String(i + 1));
          ev.push({ t: t, kind: "bar", main: String(i + 1), pip: i, accent: i === 0 });
          t += beat;
        }
      }
    }
    return { events: ev, end: t, pips: pips, meter: meter };
  }

  // ---------- the ticks that carry on after the count ----------
  // state = { next: time of the next beat, i: beat number }. Returns the ticks
  // that fall before "until" and moves the state forward.
  function nextTicks(meter, state, until) {
    var out = [];
    while (state.next < until) {
      var strong = (state.i % meter.n) === 0;
      out.push({ at: state.next, freq: strong ? 1600 : 1000, vol: 0.25, dur: 0.06 });
      if (meter.cut) out.push({ at: state.next + meter.beat / 2, freq: 800, vol: 0.12, dur: 0.05 });
      state.next += meter.beat;
      state.i++;
    }
    return out;
  }

  // ---------- sound ----------
  function tone(freq, start, dur, vol, type) {
    var o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type;
    o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, start);
    g.gain.exponentialRampToValueAtTime(vol, start + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    o.connect(g); g.connect(ctx.destination);
    o.onended = function () { var k = live.indexOf(o); if (k > -1) live.splice(k, 1); };
    o.start(start); o.stop(start + dur + 0.05);
    live.push(o);
  }
  function schedule(events, base) {
    events.forEach(function (e) {
      var at = base + e.t;
      if (e.kind === "note") tone(e.freq, at, 1.6, 0.35, "sine");
      else if (e.kind === "lead") tone(e.accent ? 1600 : 1000, at, 0.06, 0.2, "square");
      else if (e.kind === "bar") {
        if (e.offbeat) tone(800, at, 0.05, 0.12, "square");
        else tone(e.accent ? 1600 : 1000, at, 0.06, 0.25, "square");
      }
    });
  }
  function startTicks(meter, startAt) {
    var state = { next: startAt, i: 0 };
    function pump() {
      nextTicks(meter, state, ctx.currentTime + 0.3).forEach(function (k) {
        tone(k.freq, k.at, k.dur, k.vol, "square");
      });
    }
    pump();
    ticker = setInterval(pump, 50);
  }

  // ---------- the front layer ----------
  var CSS =
    "#cue-overlay{position:fixed;inset:0;z-index:3000;display:flex;flex-direction:column;align-items:center;" +
    "justify-content:center;gap:2vh;cursor:pointer;" +
    "background:color-mix(in srgb,var(--bg-color,#fff) 78%,transparent);" +   /* 🔧 TUNE: 78% = how much of the song shows through */
    "-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);}" +
    "#cue-overlay[hidden]{display:none;}" +
    "#cue-overlay .cue-main{font-size:min(38vw,42vh);font-weight:800;line-height:1;color:var(--text-color,#111);}" +
    "#cue-overlay .cue-main.k-lead{color:var(--muted,#888);}" +
    "#cue-overlay .cue-main.k-lead.accent{color:color-mix(in srgb,var(--accent,#ff8c00) 55%,var(--muted,#888));}" +
    "#cue-overlay .cue-main.k-note,#cue-overlay .cue-main.accent{color:var(--accent,#ff8c00);}" +
    "#cue-overlay .cue-sub{font-size:min(5vw,5vh);opacity:.7;min-height:1.3em;}" +
    "#cue-overlay .cue-pips{display:flex;gap:min(2.5vw,2.5vh);min-height:min(11vw,11vh);}" +
    "#cue-overlay .cue-pip{min-width:min(9vw,9vh);padding:0 .4em;text-align:center;border-radius:999px;" +
    "border:3px solid currentColor;opacity:.35;font-size:min(6vw,6vh);font-weight:700;line-height:1.6;}" +
    "#cue-overlay .cue-pip.on{opacity:1;background:var(--accent,#ff8c00);border-color:var(--accent,#ff8c00);color:#000;}" +
    "#cue-overlay .cue-hint{position:absolute;bottom:3vh;font-size:min(3.5vw,3.5vh);opacity:.5;}" +
    "@keyframes cue-pop{from{transform:scale(1.35);opacity:.35;}to{transform:scale(1);opacity:1;}}" +
    "#cue-overlay .cue-main.pop{animation:cue-pop .22s ease-out;}" +
    "@media (prefers-reduced-motion:reduce){#cue-overlay .cue-main.pop{animation:none;}}";

  function ensureOverlay() {
    if (overlay) return;
    var st = document.createElement("style");
    st.textContent = CSS;
    document.head.appendChild(st);

    overlay = document.createElement("div");
    overlay.id = "cue-overlay";
    overlay.hidden = true;
    overlay.setAttribute("role", "status");
    overlay.innerHTML =
      '<div class="cue-main"></div><div class="cue-sub"></div>' +
      '<div class="cue-pips"></div><div class="cue-hint">Tap anywhere to cancel</div>';
    document.body.appendChild(overlay);
    parts = {
      main: overlay.querySelector(".cue-main"),
      sub: overlay.querySelector(".cue-sub"),
      pips: overlay.querySelector(".cue-pips"),
    };
    overlay.addEventListener("click", stopAll);
  }

  function show(e) {
    parts.main.textContent = e.main;
    parts.main.className = "cue-main k-" + e.kind + (e.accent ? " accent" : "");
    void parts.main.offsetWidth;                 // restart the pop animation
    parts.main.classList.add("pop");
    parts.sub.textContent = e.sub || "";
    var lit = (e.pip !== undefined) ? e.pip : -1;
    Array.prototype.forEach.call(parts.pips.children, function (el, i) {
      el.classList.toggle("on", i === lit);
    });
  }

  // ---------- the Cue button: Cue <-> Stop ----------
  function setButton(ticking) {
    var btn = document.getElementById("cue-btn");
    if (!btn) return;
    btn.innerHTML = ticking
      ? '⏹<span class="cue-label"> Stop</span>'
      : '🎵<span class="cue-label"> Cue</span>';
    btn.title = ticking ? "Stop the ticks" : "Cue: play the first note, then the count-in";
    btn.setAttribute("aria-pressed", ticking ? "true" : "false");
  }

  // ---------- run / stop ----------
  function stopAll() {
    cancelAnimationFrame(raf);
    clearInterval(ticker);
    live.slice().forEach(function (o) { try { o.stop(); } catch (e) {} });
    live = [];
    running = false;
    if (overlay) overlay.hidden = true;
    setButton(false);
  }

  function run(cue) {
    ensureOverlay();
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === "suspended") ctx.resume();

    var tv = document.getElementById("transpose-value");
    var shift = tv ? parseInt(tv.textContent, 10) || 0 : 0;
    var seq = buildSequence(cue, shift);
    if (!seq.events.length) return;

    running = true;
    setButton(true);

    parts.pips.innerHTML = "";
    seq.pips.forEach(function (label) {
      var d = document.createElement("div");
      d.className = "cue-pip";
      d.textContent = label;
      parts.pips.appendChild(d);
    });

    var base = ctx.currentTime + 0.1, idx = -1;
    schedule(seq.events, base);
    if (seq.meter) startTicks(seq.meter, base + seq.end);   // the ticks carry on after the count
    overlay.hidden = false;

    // The screen follows the audio clock, so the numbers land with the clicks.
    (function frame() {
      var now = ctx.currentTime - base;
      var next = idx;
      while (next + 1 < seq.events.length && seq.events[next + 1].t <= now) next++;
      if (next !== idx) { idx = next; show(seq.events[idx]); }
      if (now >= seq.end) {
        overlay.hidden = true;                 // no visuals once the song starts
        if (!seq.meter) stopAll();             // first note only: nothing left to play
        return;                                // with a tempo: ticks go on until Stop
      }
      raf = requestAnimationFrame(frame);
    })();
  }

  // ---------- wiring ----------
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("cue-btn");
    var dataEl = document.getElementById("cue-data");
    if (!btn || !dataEl) return;

    var cue = null;
    try { cue = JSON.parse(dataEl.textContent); } catch (e) {}
    if (!cue) return;                       // no tempo or first note: button stays hidden
    btn.hidden = false;
    btn.addEventListener("click", function () {
      if (running) stopAll();               // pressing Cue again stops the ticks
      else run(cue);
    });
  });

  if (typeof module !== "undefined") module.exports = { buildSequence: buildSequence, nextTicks: nextTicks };
})();