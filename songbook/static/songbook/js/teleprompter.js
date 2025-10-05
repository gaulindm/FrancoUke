/* teleprompter.js
   - Robust teleprompter scrolling (requestAnimationFrame)
   - Toggles chord diagrams
   - Swipe navigation between songs
   - Auto-hide overlay controls
   - Responsive lyrics container sizing
   - Scroll speed control (+ / - / Save)
*/

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);

  // --- State ---
  let rafId = null;
  let lastRafTime = null;
  let isAutoScrolling = false;

  // scroll_speed now directly represents pixels/second
  let speedSetting = window.initialScrollSpeed || 40;

  // --- Speed range and control ---
  const SPEED_STEP = 5;
  const MIN_SPEED = 5;
  const MAX_SPEED = 300;

// --- Utility ---
function pixelsPerSecond() {
  return Math.max(MIN_SPEED, Math.min(speedSetting, MAX_SPEED));
}

function updateSpeedDisplay() {
  const disp = $("#scroll-speed-display");
  if (disp) disp.textContent = `${Math.round(speedSetting)} px/s`;
}

  function getCSRFToken() {
    const name = "csrftoken";
    const cookie = document.cookie.split(";").find(c => c.trim().startsWith(name + "="));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
  }

  // --- Scrolling Engine ---
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

  let scrollAccumulator = 0;

  function stepScroll(ts) {
    if (!lastRafTime) lastRafTime = ts;
    const dt = (ts - lastRafTime) / 1000;
    lastRafTime = ts;
  
    const c = $(".lyrics-container");
    if (!c) return stopScroll();
  
    scrollAccumulator += pixelsPerSecond() * dt;
  
    const whole = Math.floor(scrollAccumulator);
    if (whole !== 0) {
      c.scrollTop = Math.min(
        c.scrollTop + whole,
        c.scrollHeight - c.clientHeight
      );
      scrollAccumulator -= whole;
    }
  
    if (c.scrollTop + c.clientHeight >= c.scrollHeight - 0.5) return stopScroll();
    rafId = requestAnimationFrame(stepScroll);
  }
  

  function startScroll() {
    if (isAutoScrolling) return;
    const c = $(".lyrics-container");
    if (!c || c.scrollHeight <= c.clientHeight) return;
    isAutoScrolling = true;
    lastRafTime = null;
    rafId = requestAnimationFrame(stepScroll);
    $("#scroll-toggle").textContent = "⏸ Pause";
  }

  function stopScroll() {
    if (!isAutoScrolling) return;
    cancelAnimationFrame(rafId);
    rafId = null;
    isAutoScrolling = false;
    $("#scroll-toggle").textContent = "▶️ Start";
  }

  function resetScroll() {
    stopScroll();
    $(".lyrics-container")?.scrollTo({ top: 0, behavior: "smooth" });
  }

  function bindPauseOnUserScroll(c) {
    if (!c) return;
    const pause = () => isAutoScrolling && stopScroll();
    c.addEventListener("touchstart", pause, { passive: true });
    c.addEventListener("wheel", pause, { passive: true });
    c.addEventListener("pointerdown", pause, { passive: true });
  }

  // --- Chords ---
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
    $("#chord-section").classList.toggle("hidden");
    $("#toggle-chords").textContent = $("#chord-section").classList.contains("hidden")
      ? "Show Chords"
      : "Hide Chords";
    setTimeout(updateLyricsContainerHeight, 60);
    if (!$("#chord-section").classList.contains("hidden") && window.SONG?.chords)
      renderChordDiagrams(window.SONG.chords);
  }

  // --- Swipe ---
  let touchStartX = 0;
  document.addEventListener("touchstart", (e) => (touchStartX = e.touches[0].screenX), { passive: true });
  document.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].screenX - touchStartX;
    if (dx < -50) window.location.href = $("#nav-overlay .right")?.href || "#";
    if (dx > 50) window.location.href = $("#nav-overlay .left")?.href || "#";
  }, { passive: true });

  // --- Overlay ---
  let overlayTimer = null;
  function showOverlay() {
    $("#nav-overlay")?.classList.remove("hidden");
    clearTimeout(overlayTimer);
    overlayTimer = setTimeout(() => $("#nav-overlay")?.classList.add("hidden"), 3000);
  }

  // --- Init ---
  document.addEventListener("DOMContentLoaded", () => {
    // Main controls
    $("#scroll-toggle")?.addEventListener("click", () => (isAutoScrolling ? stopScroll() : startScroll()));
    $("#scroll-reset")?.addEventListener("click", resetScroll);
    $("#toggle-chords")?.addEventListener("click", toggleChordSection);

    // --- Speed Control ---
    updateSpeedDisplay();
    const decBtn = $("#speed-decrease");
    const incBtn = $("#speed-increase");
    const saveBtn = $("#speed-save");

    if (decBtn && incBtn) {
      decBtn.addEventListener("click", () => {
        speedSetting = Math.max(MIN_SPEED, speedSetting - SPEED_STEP);
        updateSpeedDisplay();
      });

      incBtn.addEventListener("click", () => {
        speedSetting = Math.min(MAX_SPEED, speedSetting + SPEED_STEP);
        updateSpeedDisplay();
      });
    }

    if (saveBtn) {
      saveBtn.addEventListener("click", async () => {
        if (!window.SONG?.id) {
          alert("No song loaded.");
          return;
        }
    
        try {
          const response = await fetch(`/songs/${window.SONG.id}/set-scroll-speed/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ scroll_speed: Math.round(speedSetting) }),
          });
    
          if (!response.ok) throw new Error(`Server error: ${response.status}`);
    
          const result = await response.json().catch(() => ({}));
          console.log("✅ Scroll speed saved:", result);
    
          saveBtn.textContent = "✅ Saved";
          setTimeout(() => (saveBtn.textContent = "💾 Save"), 1500);
        } catch (err) {
          console.error("⚠️ Error saving scroll speed:", err);
          alert("⚠️ Error saving scroll speed. Please try again.");
        }
      });
    }
    

    // Layout & interactions
    updateLyricsContainerHeight();
    window.addEventListener("resize", updateLyricsContainerHeight, { passive: true });
    window.addEventListener("orientationchange", () => setTimeout(updateLyricsContainerHeight, 200));

    bindPauseOnUserScroll($(".lyrics-container"));

    // Chords JSON load
    const chordEl = [...document.querySelectorAll("#chords-data")].pop();
    if (chordEl) {
      try {
        const chords = JSON.parse(chordEl.textContent);
        window.SONG = { ...window.SONG, chords };
        if (!$("#chord-section").classList.contains("hidden")) renderChordDiagrams(chords);
      } catch (e) {
        console.error("Chord JSON parse error:", e);
      }
    }

    // Overlay
    if ($("#nav-overlay")) {
      showOverlay();
      ["mousemove", "touchstart", "click"].forEach((evt) =>
        document.addEventListener(evt, showOverlay, { passive: true })
      );
    }
  }); // <-- closes DOMContentLoaded
})(); // <-- closes IIFE