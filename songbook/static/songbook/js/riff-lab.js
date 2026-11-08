// Riff Lab page: for every melody ("riff") card on the page, draws the notation + ukulele tab
// and adds Play (nylon guitar), Speed 50/75/100 %, Repeat, and a red highlight that follows the notes.
// Needs abcjs, abc-tab.js and (per card) data-abc and optionally data-tempo.
(function () {
    var PROGRAM = 24;          // General MIDI 24 = nylon-string guitar
    var FALLBACK_QPM = 100;    // used when neither the riff (Q:) nor the song ({tempo:}) gives a tempo
    var SCALE = 1.8;           // notation size
    var audioCtx = null;
    var active = null;         // the playback in progress: { card, synth, timer, stop }
  
    function baseQpm(card, abc) {
      var m = /^Q:\s*(?:\d+\/\d+\s*=\s*)?(\d+)/m.exec(abc);          // the riff's own Q: line wins
      if (m) return parseInt(m[1], 10);
      var t = parseInt(card.dataset.tempo, 10);                       // then the song's {tempo:}
      return t > 20 && t < 300 ? t : FALLBACK_QPM;
    }
  
    function setupCard(card) {
      var abc = card.dataset.abc || '';
      var paper = card.querySelector('.riff-paper');
      var playBtn = card.querySelector('.riff-play');
      var loop = card.querySelector('.riff-loop input');
      var msg = card.querySelector('.riff-msg');
      var factor = 1;
  
      var src = /^X:/m.test(abc) ? abc : 'X:1\n' + abc;
      var tunes = ABCJS.renderAbc(paper, src, { responsive: 'resize', add_classes: true, scale: SCALE });
      var tune = tunes && tunes[0];
      if (!tune) { msg.textContent = '⚠ This melody could not be read.'; playBtn.disabled = true; return; }
      if (window.AbcTab && !/^%%notab\s*$/m.test(abc)) {
        try { window.AbcTab.draw(tune, paper, SCALE); } catch (e) { if (window.console) console.warn('Uke tab failed:', e); }
      }
  
      function clearHighlight() {
        paper.querySelectorAll('.rl-playing').forEach(function (n) { n.classList.remove('rl-playing'); });
      }
      function idle() { playBtn.textContent = '▶ Play'; playBtn.disabled = false; playBtn.classList.remove('playing'); }
  
      function stop() {
        var r = active; if (!r || r.card !== card) { clearHighlight(); idle(); return; }
        active = null;
        try { r.synth.stop(); } catch (e) {}
        try { r.timer && r.timer.stop(); } catch (e) {}
        clearHighlight(); idle();
      }
  
      function play() {
        if (active) { var other = active; other.stop(); }       // only one riff plays at a time
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) { msg.textContent = '⚠ This device cannot play sound.'; return; }
        if (!audioCtx) audioCtx = new AC();                     // created inside the tap, as iOS requires
        try { audioCtx.resume(); } catch (e) {}
        msg.textContent = '';
        playBtn.disabled = true; playBtn.textContent = '… Loading';
  
        var qpm = Math.max(20, Math.round(baseQpm(card, abc) * factor));
        var synth = new ABCJS.synth.CreateSynth();
        var me = { card: card, synth: synth, timer: null, stop: stop };
        active = me;
        synth.init({
          audioContext: audioCtx,
          visualObj: tune,
          options: {
            program: PROGRAM,
            qpm: qpm,
            onEnded: function () {
              if (active !== me) return;
              if (me.timer) { try { me.timer.stop(); } catch (e) {} }
              clearHighlight(); active = null; idle();
              if (loop.checked) play();                         // Repeat
            }
          }
        }).then(function () { return synth.prime(); })
          .then(function () {
            if (active !== me) return;                          // stopped while loading
            playBtn.disabled = false; playBtn.textContent = '⏹ Stop'; playBtn.classList.add('playing');
            me.timer = new ABCJS.TimingCallbacks(tune, {
              qpm: qpm,
              eventCallback: function (ev) {
                clearHighlight();
                if (!ev) return;
                (ev.elements || []).forEach(function (g) {
                  [].concat(g).forEach(function (n) { if (n && n.classList) n.classList.add('rl-playing'); });
                });
              }
            });
            synth.start();
            me.timer.start();
          }).catch(function (err) {
            if (window.console) console.warn('Riff Lab playback failed:', err);
            if (active === me) active = null;
            idle();
            msg.textContent = '⚠ The sound could not be loaded (an internet connection is needed).';
          });
      }
  
      playBtn.addEventListener('click', function () { (active && active.card === card) ? stop() : play(); });
      card.querySelectorAll('.riff-speed button').forEach(function (b) {
        b.addEventListener('click', function () {
          factor = parseFloat(b.dataset.f);
          card.querySelectorAll('.riff-speed button').forEach(function (x) { x.classList.toggle('on', x === b); });
          if (active && active.card === card) { stop(); play(); }   // new speed applies straight away
        });
      });
    }
  
    document.addEventListener('DOMContentLoaded', function () {
      if (!window.ABCJS) return;
      document.querySelectorAll('.riff-card').forEach(setupCard);
    });
    window.addEventListener('pagehide', function () { if (active) active.stop(); });
  })();