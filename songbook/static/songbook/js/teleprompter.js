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
  let scrollPos = 0;

  const SLOWER_SCALE = 0.5;
  window.userPreferences = {};

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
    scrollPos += actualSpeed * dt;

    const maxTop = Math.max(0, c.scrollHeight - c.clientHeight);
    if (scrollPos > maxTop) scrollPos = maxTop;

    c.scrollTop = scrollPos;
    if (scrollPos >= maxTop - 0.5) {
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

// --- 🎸 Lookup a chord by cleaned name ---
function findChord(chordName) {
  if (!window.CLEANED_CHORD_LIBRARY?.length) return null;
  const cleaned = cleanChordName(chordName);
  return window.CLEANED_CHORD_LIBRARY.find(
    (ch) => ch.cleanedName === cleaned
  );
}


  // -----------------------------
  // 🎵 Chord Rendering
  // -----------------------------
  function renderChordDiagrams(chords) {
    const cont = $("#chord-diagrams");
    if (!cont) return;
    cont.innerHTML = "";
    const prefs = window.userPreferences || {};
    const showAlternate = !!prefs.showAlternate;
  
    chords.forEach((chord) => {
      const match = findChord(chord.name);
      if (!match) {
        console.warn(`⚠️ No matching chord found for "${chord.name}" → "${cleanChordName(chord.name)}"`);
        return;
      }
  
      const vars = showAlternate
        ? match.variations
        : [match.variations[0]];
  
      vars.forEach((v) => {
        const wrap = document.createElement("div");
        wrap.className = "chord-wrapper";
        if (typeof drawChordDiagram === "function")
          drawChordDiagram(wrap, { name: chord.name, ...v });
        cont.appendChild(wrap);
      });
    });
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
  // Layout adjust
  // -----------------------------
  function updateLyricsContainerHeight() {
    const container = $(".lyrics-container");
    if (!container) return;
    const controlsH = $(".controls")?.getBoundingClientRect().height || 0;
    const chordH = !$("#chord-section")?.classList.contains("hidden")
      ? $("#chord-section").getBoundingClientRect().height
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
    const saveBtn = $("#speed-save") || $("#save-speed");
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

    saveBtn?.addEventListener("click", async () => {
      if (!window.SONG?.id) return alert("No song loaded.");
      try {
        const res = await fetch(`/songs/${window.SONG.id}/set-scroll-speed/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ scroll_speed: Math.round(scrollSpeed) }),
        });
        if (!res.ok) throw new Error(res.statusText);
        saveBtn.textContent = "✅ Saved";
        setTimeout(() => (saveBtn.textContent = "💾 Save"), 1500);
      } catch (err) {
        console.error("Save failed", err);
        alert("Error saving scroll speed.");
      }
    });

    toggleBtn?.addEventListener("click", () =>
      isAutoScrolling ? stopScroll() : startScroll()
    );
    resetBtn?.addEventListener("click", resetScroll);
    toggleChordsBtn?.addEventListener("click", toggleChordSection);

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

    // Overlay handling
    const overlay = $("#nav-overlay");
    if (overlay) {
      overlay.classList.remove("hidden");
      ["mousemove", "touchstart", "click"].forEach(evt =>
        document.addEventListener(evt, () => overlay.classList.remove("hidden"), { passive: true })
      );
      setTimeout(() => overlay.classList.add("hidden"), 3000);
    }

    // Tap gestures
    const lyrics = $(".lyrics-container");
    if (lyrics) {
      let lastTap = 0;
      lyrics.addEventListener("touchend", e => {
        const now = Date.now();
        const delta = now - lastTap;
        lastTap = now;
        if (delta < 300) toggleChordSection();
        else isAutoScrolling ? stopScroll() : startScroll();
      }, { passive: true });
    }
  });

  window.teleprompter = {
    start: startScroll,
    stop: stopScroll,
    setSpeed: v => {
      scrollSpeed = v;
      updateSpeedDisplay();
    },
  };
})();
