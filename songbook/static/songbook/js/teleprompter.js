/* teleprompter.js
   Robust version (Option A) — compatible with Django backend
   Features:
   - Smooth scroll (px/sec, requestAnimationFrame)
   - User preferences loaded from DOM
   - Chord diagrams rendered from embedded JSON
   - Handles slash chords like [Em///], [D/F#], [Cmaj7]
   - Works with ukulele, banjo, baritone_ukulele, etc.
*/

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);

  // -----------------------------
  // Defaults and state
  // -----------------------------
  let scrollSpeed = 30; // px/sec
  let isAutoScrolling = false;
  let rafId = null;
  let lastRafTime = null;
  window.scrollPos = 0;

  const SLOWER_SCALE = 0.5;
  window.userPreferences = {};

  const CHORD_LAYOUT_KEY = "tp-chord-layout"; // "bottom" | "right"
  const TRANSPOSE_KEY = "tp-transpose-steps"; // integer semitone offset, per-browser

  // -----------------------------
  // Config loader
  // -----------------------------
  function loadConfigFromDom() {
    try {
      const cfgEl = document.getElementById("teleprompter-config");
      if (cfgEl) {
        const cfg = JSON.parse(cfgEl.textContent);
        if (typeof cfg.initialScrollSpeed === "number")
          scrollSpeed = cfg.initialScrollSpeed;
        if (cfg.userPreferences)
          window.userPreferences = cfg.userPreferences;
        console.log("⚙️ teleprompter-config loaded:", {
          scrollSpeed,
          userPreferences: window.userPreferences,
        });
      }
    } catch (e) {
      console.warn("⚠️ Failed to parse teleprompter-config JSON", e);
    }
  }

  // -----------------------------
  // CSRF helper for save button
  // -----------------------------
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  // -----------------------------
  // Scroll control
  // -----------------------------
  function stepScroll(ts) {
    if (!lastRafTime) lastRafTime = ts;
    const dt = (ts - lastRafTime) / 1000;
    lastRafTime = ts;

    const c = $(".lyrics-container");
    if (!c) {
      stopScroll();
      return;
    }

    const actualSpeed = Math.max(0.1, scrollSpeed) * 6 * SLOWER_SCALE;
    window.scrollPos += actualSpeed * dt;

    const maxTop = Math.max(0, c.scrollHeight - c.clientHeight);
    if (window.scrollPos > maxTop) window.scrollPos = maxTop;

    c.scrollTop = window.scrollPos;
    if (window.scrollPos >= maxTop - 0.5) {
      stopScroll();
      return;
    }

    rafId = requestAnimationFrame(stepScroll);
  }

  function startScroll() {
    if (isAutoScrolling) return;
    const c = $(".lyrics-container");
    if (!c || c.scrollHeight <= c.clientHeight) return;

    isAutoScrolling = true;
    lastRafTime = null;
    scrollPos = c.scrollTop;
    rafId = requestAnimationFrame(stepScroll);

    const toggle = $("#scroll-toggle");
    if (toggle) {
      toggle.textContent = "⏸ Pause";
      toggle.classList.add("active");
    }
  }

  function stopScroll() {
    if (!isAutoScrolling) return;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
    isAutoScrolling = false;

    const toggle = $("#scroll-toggle");
    if (toggle) {
      toggle.textContent = "▶️ Start";
      toggle.classList.remove("active");
    }
  }

  function resetScroll() {
    stopScroll();
    $(".lyrics-container")?.scrollTo({ top: 0, behavior: "smooth" });
  }

  // -----------------------------
  // Pause when user touches/scrolls
  // -----------------------------
  function bindPauseOnUserScroll(c) {
    if (!c) return;
    const pause = () => isAutoScrolling && stopScroll();
    c.addEventListener("touchstart", pause, { passive: true });
    c.addEventListener("wheel", pause, { passive: true });
    c.addEventListener("pointerdown", pause, { passive: true });
  }

  // -----------------------------
  // Speed display
  // -----------------------------
  function getSpeedDisplayEl() {
    return $("#speed-value") || $("#scroll-speed-display") || $("#speed-display");
  }

  function updateSpeedDisplay() {
    const disp = getSpeedDisplayEl();
    if (disp) disp.textContent = `${Math.round(scrollSpeed)} px/s`;
  }

  // -----------------------------
  // 🧠 Chord name cleaning
  // -----------------------------
  function cleanChordName(chord) {
    if (!chord) return "";
    chord = chord.replace(/^\[|\]$/g, "").trim(); // remove [ ]
    chord = chord.replace(/\/+$/g, "");           // remove trailing ///
    chord = chord.replace(/\/[A-G][#b]?$/i, "");  // remove bass note
    chord = chord.replace(/maj/i, "M").replace(/Δ/g, "M");
    return chord.toUpperCase();
  }

  // -----------------------------
  // 🧠 Chord Library Helpers
  // -----------------------------
  function buildCleanedChordLibrary(data) {
    return data.map(ch => ({
      ...ch,
      cleanedName: cleanChordName(ch.name),
    }));
  }

  // --- 🎸 Lookup a chord by cleaned name ---
  function findChord(chordName) {
    if (!window.CLEANED_CHORD_LIBRARY?.length) {
      console.warn("⚠️ Chord library not loaded yet.");
      return null;
    }

    const cleaned = cleanChordName(chordName);
    const match = window.CLEANED_CHORD_LIBRARY.find(
      (ch) => ch.cleanedName === cleaned
    );

    if (!match) {
      console.warn(`⚠️ No chord match found for "${chordName}" → "${cleaned}"`);
    }

    return match || null;
  }

  // --- 🎸 Simple Chord Library Loader (no fetch, uses embedded JSON) ---
  async function loadChordLibrary(instrument = "ukulele") {
    try {
      const embedded = document.getElementById("chords-data");
      if (!embedded) {
        console.warn("⚠️ No embedded chord JSON found — skipping loadChordLibrary");
        window.CHORD_LIBRARY = [];
        return;
      }

      const data = JSON.parse(embedded.textContent);
      window.CHORD_LIBRARY = data;
      window.CLEANED_CHORD_LIBRARY = data.map(ch => ({
        ...ch,
        cleanedName: cleanChordName(ch.name),
      }));

      console.log(`✅ Loaded ${data.length} chords from embedded data`);
    } catch (err) {
      console.error("❌ Failed to parse embedded chord JSON:", err);
      window.CHORD_LIBRARY = [];
      window.CLEANED_CHORD_LIBRARY = [];
    }
  }

  // -----------------------------
  // 🎵 Chord Rendering
  // -----------------------------
  function renderChordDiagrams(chords) {
    const cont = $("#chord-diagrams");
    if (!cont) return;
    cont.innerHTML = "";
  
    chords.forEach((chord) => {
      // The variations are already correctly selected by the backend
      const variations = chord.variations || [];
      
      // Render ALL variations that were sent from the backend
      variations.forEach((v, idx) => {
        const wrap = document.createElement("div");
        wrap.className = "chord-wrapper";
        if (typeof drawChordDiagram === "function")
          drawChordDiagram(wrap, { name: chord.name, ...v, variation_index: idx });
        cont.appendChild(wrap);
      });
    });
  }

  // -----------------------------
  // 🎼 Transpose
  // -----------------------------
  // This shifts each chord *shape* up/down the neck by N frets (the same
  // trick a capo uses), rather than looking up a fresh "textbook" open
  // shape for the new chord name. That means it works entirely offline,
  // with zero calls back to Django, using only the chord shapes already
  // embedded on the page for this song. The trade-off: a chord you'd
  // normally finger as an open shape may show up as a small barre once
  // transposed, instead of the open-position fingering the PDF/admin tool
  // would pick. The chord *names* shown above the lyrics are always
  // correct either way.
  // Ported directly from songbook/utils/transposer.py's transpose_chord()
  // so a chord shown here always matches what the same shift produces in
  // your PDFs/admin tool.
  const NOTES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  const NOTES_FLAT  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
  const ENHARMONIC_EQUIVALENTS = {
    "B#": "C", "E#": "F", "Cb": "B", "Fb": "E",
    "A#": "Bb", "D#": "Eb", "G#": "G#",
    "Bb": "A#", "Eb": "D#", "Ab": "G#",
  };
  const TRANSPOSE_MIN = -11;
  const TRANSPOSE_MAX = 11;

  function normalizeChord(note) {
    return Object.prototype.hasOwnProperty.call(ENHARMONIC_EQUIVALENTS, note)
      ? ENHARMONIC_EQUIVALENTS[note]
      : note;
  }

  // Mirrors transpose_chord()'s root-handling exactly: pre-map the root
  // through ENHARMONIC_EQUIVALENTS to pick which scale (sharp/flat) to
  // index into, then normalize the result the same way on the way out.
  function transposeNoteName(root, steps) {
    if (!NOTES_SHARP.includes(root) && !NOTES_FLAT.includes(root)) return root;
    if (Object.prototype.hasOwnProperty.call(ENHARMONIC_EQUIVALENTS, root)) {
      root = ENHARMONIC_EQUIVALENTS[root];
    }
    const notes = NOTES_SHARP.includes(root) ? NOTES_SHARP : NOTES_FLAT;
    const newIdx = ((notes.indexOf(root) + steps) % 12 + 12) % 12;
    return normalizeChord(notes[newIdx]);
  }

  let transposeSteps = 0;
  let originalChordLabels = []; // [{ el, name }] captured once at page load
  let originalSongChords = null; // deep copy of window.SONG.chords as first loaded

  // Splits "D/F#", "Cmaj7", "F#m7b5" into { root, suffix, bass }
  function splitChordName(name) {
    const m = (name || "").match(/^([A-G][b#]?)(.*)$/);
    if (!m) return { root: name || "", suffix: "", bass: "" };
    let [, root, rest] = m;
    let bass = "";
    const bassMatch = rest.match(/\/([A-G][b#]?)$/);
    if (bassMatch) {
      bass = bassMatch[1];
      rest = rest.slice(0, -bassMatch[0].length);
    }
    return { root, suffix: rest, bass };
  }

  function transposeChordName(name, steps) {
    if (!steps || !name) return name;
    const { root, suffix, bass } = splitChordName(name);
    const newRoot = transposeNoteName(root, steps);
    const newBass = bass ? transposeNoteName(bass, steps) : "";
    return newRoot + suffix + (newBass ? "/" + newBass : "");
  }

  // Shifts a set of fretted string positions by N frets (capo-style).
  // -1 (muted string) is left untouched; anything that would go below
  // fret 0 wraps up an octave (+12) so it stays on the fretboard.
  function transposePositions(positions, steps) {
    return (positions || []).map((f) => {
      if (f === -1) return -1;
      let shifted = f + steps;
      while (shifted < 0) shifted += 12;
      return shifted;
    });
  }

  // One-time snapshot of the page's untransposed state, so every transpose
  // is computed fresh from the original (never compounded/rounded away).
  function captureTransposeBaseline() {
    // [data-chord] matches both render modes: chord_position="above"
    // (<span class="chord-label" data-chord="C">C</span>) and the
    // chord_position="inline" your teleprompter.html actually uses
    // (<b class="chord-token" data-chord="C">[C]</b>). The attribute
    // always holds the bare chord name even where the visible text
    // includes brackets, so we capture the template text once and
    // substring-replace into it rather than assuming a format.
    originalChordLabels = Array.from(document.querySelectorAll("[data-chord]")).map((el) => ({
      el,
      chord: el.dataset.chord,
      template: el.textContent,
    }));
    originalSongChords = window.SONG?.chords
      ? JSON.parse(JSON.stringify(window.SONG.chords))
      : null;
  }

  function applyTranspose(steps) {
    steps = Math.max(TRANSPOSE_MIN, Math.min(TRANSPOSE_MAX, steps));
    transposeSteps = steps;

    // 1. Chord names shown above/inline with the lyrics
    originalChordLabels.forEach(({ el, chord, template }) => {
      const newChord = transposeChordName(chord, steps);
      el.textContent = template.replace(chord, newChord);
      el.dataset.chord = newChord;
    });

    // 2. Chord diagrams — shift each variation's shape, then re-render
    if (originalSongChords) {
      const transposed = originalSongChords.map((ch) => ({
        ...ch,
        name: transposeChordName(ch.name, steps),
        variations: (ch.variations || []).map((v) => {
          const positions = transposePositions(v.positions, steps);
          return { ...v, positions, baseFret: computeBaseFret(positions) };
        }),
      }));
      window.SONG.chords = transposed;
      const section = $("#chord-section");
      if (section && !section.classList.contains("hidden")) {
        renderChordDiagrams(transposed);
      }
    }

    const display = $("#transpose-value");
    if (display) display.textContent = steps > 0 ? `+${steps}` : `${steps}`;

    const downBtn = $("#transpose-down"), upBtn = $("#transpose-up");
    if (downBtn) downBtn.disabled = steps <= TRANSPOSE_MIN;
    if (upBtn) upBtn.disabled = steps >= TRANSPOSE_MAX;

    try {
      localStorage.setItem(TRANSPOSE_KEY, String(steps));
    } catch (e) {
      // localStorage unavailable — transpose just won't be remembered next visit.
    }
  }

  function toggleChordSection() {
    const section = $("#chord-section");
    if (!section) return;
    section.classList.toggle("hidden");

    const btn = $("#toggle-chords");
    if (btn)
      btn.textContent = section.classList.contains("hidden")
        ? "Show Chords"
        : "Hide Chords";

    setTimeout(updateLyricsContainerHeight, 60);
    if (!section.classList.contains("hidden") && window.SONG?.chords)
      renderChordDiagrams(window.SONG.chords);
  }

  // -----------------------------
  // Chord diagram position (bottom strip vs. right sidebar)
  // -----------------------------
  function applyChordLayout(mode) {
    const isRight = mode === "right";
    document.body.classList.toggle("chords-right", isRight);

    const bottomBtn = $("#chord-layout-bottom");
    const rightBtn = $("#chord-layout-right");
    bottomBtn?.classList.toggle("active", !isRight);
    rightBtn?.classList.toggle("active", isRight);
    bottomBtn?.setAttribute("aria-pressed", String(!isRight));
    rightBtn?.setAttribute("aria-pressed", String(isRight));

    try {
      localStorage.setItem(CHORD_LAYOUT_KEY, mode);
    } catch (e) {
      // localStorage unavailable (private browsing etc.) — layout just
      // won't be remembered next visit, nothing else breaks.
    }

    // #chord-section's box changes height (bottom mode) or width-only
    // (right mode), so re-measure once the CSS transition/layout settles.
    setTimeout(updateLyricsContainerHeight, 60);
  }

  // -----------------------------
  // Layout adjust
  // -----------------------------
  function updateLyricsContainerHeight() {
    const container = $(".lyrics-container");
    if (!container) return;
    const controlsH = $(".controls")?.getBoundingClientRect().height || 0;

    // In "right" layout the chord section takes up width (handled purely
    // in CSS via .lyrics-container padding-right), not page height, so it
    // should not shrink the scroll container the way the bottom strip does.
    const isRightLayout = document.body.classList.contains("chords-right");
    const section = $("#chord-section");
    const chordH = (!isRightLayout && section && !section.classList.contains("hidden"))
      ? section.getBoundingClientRect().height
      : 0;

    const available = Math.max(120, window.innerHeight - controlsH - chordH);
    container.style.height = available + "px";
    container.style.overflowY = "auto";
    container.style.WebkitOverflowScrolling = "touch";
  }

  // -----------------------------
  // DOM Ready
  // -----------------------------
  document.addEventListener("DOMContentLoaded", async () => {
    loadConfigFromDom();

    const prefs = window.userPreferences;
    const instrument = prefs.instrument || "ukulele";
    await loadChordLibrary(instrument);

    // Bind buttons
    const decBtn = $("#speed-down"), incBtn = $("#speed-up");
    const toggleBtn = $("#scroll-toggle");
    const resetBtn = $("#scroll-reset");
    const toggleChordsBtn = $("#toggle-chords");

    updateSpeedDisplay();

    decBtn?.addEventListener("click", () => {
      scrollSpeed = Math.max(0.5, scrollSpeed - 1);
      updateSpeedDisplay();
    });
    incBtn?.addEventListener("click", () => {
      scrollSpeed = Math.min(1000, scrollSpeed + 1);
      updateSpeedDisplay();
    });


    toggleBtn?.addEventListener("click", () =>
      isAutoScrolling ? stopScroll() : startScroll()
    );
    resetBtn?.addEventListener("click", resetScroll);
    toggleChordsBtn?.addEventListener("click", toggleChordSection);

    const layoutBottomBtn = $("#chord-layout-bottom");
    const layoutRightBtn = $("#chord-layout-right");
    layoutBottomBtn?.addEventListener("click", () => applyChordLayout("bottom"));
    layoutRightBtn?.addEventListener("click", () => applyChordLayout("right"));

    let savedLayout = "bottom";
    try {
      savedLayout = localStorage.getItem(CHORD_LAYOUT_KEY) || "bottom";
    } catch (e) {
      // localStorage unavailable — default to bottom
    }
    applyChordLayout(savedLayout);

    updateLyricsContainerHeight();
    window.addEventListener("resize", updateLyricsContainerHeight, { passive: true });
    window.addEventListener("orientationchange", () =>
      setTimeout(updateLyricsContainerHeight, 200)
    );

    bindPauseOnUserScroll($(".lyrics-container"));

    // Load chords embedded in page
    const chordEl = document.getElementById("chords-data");
    if (chordEl) {
      try {
        const chords = JSON.parse(chordEl.textContent);
        window.SONG = { ...(window.SONG || {}), chords };
        if (!$("#chord-section").classList.contains("hidden"))
          renderChordDiagrams(chords);
      } catch (e) {
        console.error("Chord JSON parse error:", e);
      }
    }

    // Transpose — capture the untransposed state once chord labels and
    // window.SONG.chords both exist, then bind the +/- controls.
    captureTransposeBaseline();
    const transposeDownBtn = $("#transpose-down");
    const transposeUpBtn = $("#transpose-up");
    transposeDownBtn?.addEventListener("click", () => applyTranspose(transposeSteps - 1));
    transposeUpBtn?.addEventListener("click", () => applyTranspose(transposeSteps + 1));

    let savedTranspose = 0;
    try {
      savedTranspose = parseInt(localStorage.getItem(TRANSPOSE_KEY), 10) || 0;
    } catch (e) {
      // localStorage unavailable — default to 0 (original key)
    }
    applyTranspose(savedTranspose);

    // Overlay handling
    const overlay = $("#nav-overlay");
    if (overlay) {
      overlay.classList.remove("hidden");
      ["mousemove", "touchstart", "click"].forEach(evt =>
        document.addEventListener(evt, () => overlay.classList.remove("hidden"), { passive: true })
      );
      setTimeout(() => overlay.classList.add("hidden"), 3000);
    }

    // --- 🎯 Gesture Enhancements (moved inside DOMContentLoaded) ---
    const lyrics = $(".lyrics-container");
    if (lyrics) {
      let lastTap = 0;
      let startY = 0;
      let startX = 0;
      let endY = 0;
      let endX = 0;
      const SWIPE_THRESHOLD = 50; // px minimum swipe distance
      const TAP_ZONE_RATIO = 0.3; // left/right screen zones for prev/next

      // Capture swipe start
      lyrics.addEventListener("touchstart", (e) => {
        const touch = e.touches[0];
        startY = touch.clientY;
        startX = touch.clientX;
      }, { passive: true });

      // Capture swipe end (and taps)
      lyrics.addEventListener("touchend", (e) => {
        const now = Date.now();
        const deltaTime = now - lastTap;
        const touch = e.changedTouches[0];
        endY = touch.clientY;
        endX = touch.clientX;
        const diffY = endY - startY;
        const diffX = endX - startX;
        const absY = Math.abs(diffY);
        const absX = Math.abs(diffX);
        lastTap = now;

        // --- Double Tap (toggle chords) ---
        if (deltaTime < 300 && absX < 10 && absY < 10) {
          toggleChordSection();
          return;
        }

        // --- Swipe Up/Down to Adjust Speed ---
        if (absY > SWIPE_THRESHOLD && absY > absX) {
          if (diffY < 0) {
            // Swipe Up → Increase speed
            scrollSpeed = Math.min(1000, scrollSpeed + 1);
            console.log("⬆️ Increased scroll speed:", scrollSpeed);
          } else {
            // Swipe Down → Decrease speed
            scrollSpeed = Math.max(1, scrollSpeed - 1);
            console.log("⬇️ Decreased scroll speed:", scrollSpeed);
          }
          updateSpeedDisplay();
          return;
        }

        // --- Tap zones for previous / next song ---
        const screenWidth = window.innerWidth;
        const leftZone = screenWidth * TAP_ZONE_RATIO;
        const rightZone = screenWidth * (1 - TAP_ZONE_RATIO);

        if (absX < 10 && absY < 10) {
          if (endX < leftZone) {
            console.log("⏮️ Previous song");
            if (typeof window.navigateToPreviousSong === "function") {
              window.navigateToPreviousSong();
            } else {
              alert("Previous song not implemented yet.");
            }
          } else if (endX > rightZone) {
            console.log("⏭️ Next song");
            if (typeof window.navigateToNextSong === "function") {
              window.navigateToNextSong();
            } else {
              alert("Next song not implemented yet.");
            }
          } else {
            // --- Center Tap toggles scroll ---
            isAutoScrolling ? stopScroll() : startScroll();
          }
        }
      }, { passive: true });
    }

  }); // end DOMContentLoaded

  // --- 🎵 Navigation Helpers (global functions) ---
// --- 🎵 Navigation Helpers (match Django buttons) ---
window.navigateToNextSong = function() {
  const nextOrder = window.SONG?.next_order;
  const setlistId = window.SONG?.setlist_id;
  if (nextOrder && setlistId) {
    console.log("⏭️ Navigating to next song (setlist order):", nextOrder);
    window.location.href = `/setlists/${setlistId}/teleprompter/${nextOrder}/`;
  } else {
    alert("No next song available.");
  }
};

window.navigateToPreviousSong = function() {
  const prevOrder = window.SONG?.previous_order;
  const setlistId = window.SONG?.setlist_id;
  if (prevOrder && setlistId) {
    console.log("⏮️ Navigating to previous song (setlist order):", prevOrder);
    window.location.href = `/setlists/${setlistId}/teleprompter/${prevOrder}/`;
  } else {
    alert("No previous song available.");
  }
};


  // --- ✅ Teleprompter public API ---
  window.teleprompter = {
    start: startScroll,
    stop: stopScroll,
    setSpeed: v => {
      scrollSpeed = v;
      updateSpeedDisplay();
    },
  };
})();