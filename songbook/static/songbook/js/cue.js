(function () {
  var ctx = null;
  var COUNT_IN_ROUNDS = 2;   // 🔧 TUNE: how many times the count-in is played
  var NOTE_INDEX = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };

  function noteToFreq(note, shift) {
    var m = /^([A-G])([#b]?)(\d)?$/.exec(note);
    if (!m) return null;
    var n = NOTE_INDEX[m[1]] + (m[2] === "#" ? 1 : m[2] === "b" ? -1 : 0);
    var octave = m[3] ? parseInt(m[3], 10) : 4;   // no octave written = octave 4
    var midi = 12 * (octave + 1) + n + (shift || 0);
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  function tone(freq, start, dur, vol, type) {
    var o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type;
    o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, start);
    g.gain.exponentialRampToValueAtTime(vol, start + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    o.connect(g); g.connect(ctx.destination);
    o.start(start); o.stop(start + dur + 0.05);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("cue-btn");
    var dataEl = document.getElementById("cue-data");
    if (!btn || !dataEl) return;

    var cue = null;
    try { cue = JSON.parse(dataEl.textContent); } catch (e) {}
    if (!cue) return;                       // no tempo or first note: button stays hidden
    btn.hidden = false;

    btn.addEventListener("click", function () {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === "suspended") ctx.resume();

      var t = ctx.currentTime + 0.1, start = t;
      var tv = document.getElementById("transpose-value");
      var shift = tv ? parseInt(tv.textContent, 10) || 0 : 0;

      // 1) the first vocal note (follows the Transpose control)
      var freq = cue.note ? noteToFreq(cue.note, shift) : null;
      if (freq) { tone(freq, t, 1.6, 0.35, "sine"); t += 2.2; }

      // 2) the count-in, played twice: listen the first time (softer),
      //    join in the second. Accent on beat 1 of each round.
      if (cue.tempo) {
        var beat = 60 / cue.tempo, beats = cue.beats || 4;
        for (var round = 0; round < COUNT_IN_ROUNDS; round++) {
          var vol = (round < COUNT_IN_ROUNDS - 1) ? 0.15 : 0.3;
          for (var i = 0; i < beats; i++) {
            tone(i === 0 ? 1600 : 1000, t + i * beat, 0.06, vol, "square");
          }
          t += beats * beat;
        }
      }

      // block double-taps until it finishes
      btn.disabled = true;
      setTimeout(function () { btn.disabled = false; }, (t - start) * 1000 + 200);
    });
  });
})();