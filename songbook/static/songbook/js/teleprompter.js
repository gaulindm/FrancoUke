/* teleprompter.js
   Reworked for mobile/iPad robustness:
   - reads config after DOM ready
   - px/sec scrolling with float accumulator (no stalls)
   - frame-rate independent (requestAnimationFrame)
   - safe wiring for different button IDs
*/

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);

  // --- Defaults (declare early) ---
  let scrollSpeed = 30;            // px/sec default (can be overridden by config)
  const SLOWER_SCALE = 0.5;        // reduce global speed if device feels too fast (tweak this)
  window.userPreferences = {};     // filled from config if present

  // --- State for scrolling ---
  let rafId = null;
  let lastRafTime = null;
  let isAutoScrolling = false;
  let scrollPos = 0;               // floating accumulator (precise position)

  // --- Utility: config load (executed on DOMContentLoaded below) ---
  function loadConfigFromDom() {
    try {
      const cfgEl = document.getElementById("teleprompter-config");
      if (cfgEl) {
        const cfg = JSON.parse(cfgEl.textContent);
        if (typeof cfg.initialScrollSpeed === "number") scrollSpeed = cfg.initialScrollSpeed;
        if (cfg.userPreferences) window.userPreferences = cfg.userPreferences;
        console.log("⚙️ teleprompter-config loaded:", { initialScrollSpeed: scrollSpeed, userPreferences: window.userPreferences });
      } else {
        console.warn("⚠️ teleprompter-config element not found, using defaults.");
      }
    } catch (e) {
      console.warn("⚠️ Failed to parse teleprompter-config JSON, using defaults.", e);
    }
  }

  // --- CSRF helper (unchanged) ---
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  // --- Scrolling engine (frame-rate independent) ---
  function stepScroll(ts) {
    if (!lastRafTime) lastRafTime = ts;
    const dt = (ts - lastRafTime) / 1000; // seconds
    lastRafTime = ts;

    const c = $(".lyrics-container");
    if (!c) {
      stopScroll();
      return;
    }

    // Map user speed (1–50) to real px/sec using a multiplier.
    // For example, 1 → 6px/s, 10 → 60px/s, 50 → 300px/s
    const actualSpeed = Math.max(0.1, scrollSpeed) * 6 * SLOWER_SCALE;
    scrollPos += actualSpeed * dt;

    // clamp to available scroll range
    const maxTop = Math.max(0, c.scrollHeight - c.clientHeight);
    if (scrollPos > maxTop) scrollPos = maxTop;

    // apply to DOM
    // using scrollTop assignment is more reliable across platforms for fractional movement
    c.scrollTop = scrollPos;

    // stop if we reached the bottom
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

    // initialize
    isAutoScrolling = true;
    lastRafTime = null;
    scrollPos = c.scrollTop; // precise start position
    rafId = requestAnimationFrame(stepScroll);

    const toggle = $("#scroll-toggle");
    if (toggle) {
      toggle.textContent = "⏸ Pause";
      toggle.classList.add("active");
    }
  }

  function stopScroll() {
    if (!isAutoScrolling) return;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
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

  // --- Pause when user interacts with container (touch/wheel/pointer) ---
  function bindPauseOnUserScroll(c) {
    if (!c) return;
    const pause = () => isAutoScrolling && stopScroll();
    c.addEventListener("touchstart", pause, { passive: true });
    c.addEventListener("wheel", pause, { passive: true });
    c.addEventListener("pointerdown", pause, { passive: true });
  }

  // --- Speed display helper (supports different display IDs) ---
  function getSpeedDisplayEl() {
    return $("#speed-value") || $("#scroll-speed-display") || $("#speed-display");
  }
  function updateSpeedDisplay() {
    const disp = getSpeedDisplayEl();
    if (!disp) return;
    // If the display element is the 'display' variant, append "px/s"
    const showUnits = disp.id.includes("display") || disp.textContent.includes("px");
    disp.textContent = showUnits ? `${Math.round(scrollSpeed)} px/s` : `${Math.round(scrollSpeed)}`;
  }

  // --- Chord rendering + toggles (kept similar to your implementation) ---
  function renderChordDiagrams(chords) {
    const cont = $("#chord-diagrams");
    if (!cont) return;
    cont.innerHTML = "";
    const prefs = window.userPreferences || {};
    const showAlternate = !!prefs.showAlternate;
    chords.forEach((chord) => {
      const vars = showAlternate ? chord.variations : [chord.variations[0]];
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
    if (btn) btn.textContent = section.classList.contains("hidden") ? "Show Chords" : "Hide Chords";
    setTimeout(updateLyricsContainerHeight, 60);
    if (!section.classList.contains("hidden") && window.SONG?.chords) renderChordDiagrams(window.SONG.chords);
  }

  // --- Layout/resizing (keeps existing logic) ---
  function updateLyricsContainerHeight() {
    const container = $(".lyrics-container");
    if (!container) return;
    const controlsH = $(".controls")?.getBoundingClientRect().height || 0;
    const chordH = !$("#chord-section")?.classList.contains("hidden") ? $("#chord-section").getBoundingClientRect().height : 0;
    const available = Math.max(120, window.innerHeight - controlsH - chordH);
    container.style.height = available + "px";
    container.style.overflowY = "auto";
    container.style.WebkitOverflowScrolling = "touch";
  }

  // --- DOMContentLoaded: safe init when everything exists in DOM (esp. on iPad) ---
  document.addEventListener("DOMContentLoaded", () => {
    // load config NOW (DOM present)
    loadConfigFromDom();

    // wire controls (support both naming variants)
    const decBtn = $("#speed-down") || $("#speed-decrease");
    const incBtn = $("#speed-up") || $("#speed-increase");
    const saveBtn = $("#speed-save") || $("#save-speed");
    const toggleChordsBtn = $("#toggle-chords");
    const resetBtn = $("#scroll-reset");
    const toggleBtn = $("#scroll-toggle");

    // update initial display
    updateSpeedDisplay();

    // attach click handlers (guarded)
    decBtn?.addEventListener("click", () => {
      scrollSpeed = Math.max(0.5, scrollSpeed - 1); // allow fractional speeds
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
          headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
          body: JSON.stringify({ scroll_speed: Math.round(scrollSpeed) }),
        });
        if (!res.ok) throw new Error(res.statusText || "Save failed");
        saveBtn.textContent = "✅ Saved";
        setTimeout(() => (saveBtn.textContent = (saveBtn.id === "save-speed" ? "💾 Save" : "💾 Save")), 1500);
      } catch (err) {
        console.error("Save failed", err);
        alert("Error saving scroll speed.");
      }
    });

    toggleBtn?.addEventListener("click", () => (isAutoScrolling ? stopScroll() : startScroll()));
    resetBtn?.addEventListener("click", resetScroll);
    toggleChordsBtn?.addEventListener("click", toggleChordSection);

    // layout
    updateLyricsContainerHeight();
    window.addEventListener("resize", updateLyricsContainerHeight, { passive: true });
    window.addEventListener("orientationchange", () => setTimeout(updateLyricsContainerHeight, 200));

    // pause on user scroll interaction
    bindPauseOnUserScroll($(".lyrics-container"));

    // chords JSON load
    const chordEl = document.getElementById("chords-data");
    if (chordEl) {
      try {
        const chords = JSON.parse(chordEl.textContent);
        window.SONG = { ...(window.SONG || {}), chords };
        if (!$("#chord-section").classList.contains("hidden")) renderChordDiagrams(chords);
      } catch (e) {
        console.error("Chord JSON parse error:", e);
      }
    }

    // overlay
    const overlay = $("#nav-overlay");
    if (overlay) {
      // show once and bind activity listeners
      overlay.classList.remove("hidden");
      ["mousemove", "touchstart", "click"].forEach((evt) => document.addEventListener(evt, () => overlay.classList.remove("hidden"), { passive: true }));
      setTimeout(() => overlay.classList.add("hidden"), 3000);
    }

    // ---- Mobile tap gestures: single tap = start/stop, double tap = toggle chords ----
    const lyrics = document.querySelector(".lyrics-container");
    if (lyrics) {
      let lastTap = 0;
      lyrics.addEventListener("touchend", (e) => {
        const now = Date.now();
        const delta = now - lastTap;
        lastTap = now;
        if (delta < 300) {
          // double tap
          toggleChordSection();
        } else {
          // single tap
          if (isAutoScrolling) stopScroll();
          else startScroll();
        }
      }, { passive: true });
    }
  }); // end DOMContentLoaded

  // Expose start/stop for other scripts if needed
  window.teleprompter = {
    start: startScroll,
    stop: stopScroll,
    setSpeed: (v) => { scrollSpeed = v; updateSpeedDisplay(); },
  };

})(); // end IIFE
