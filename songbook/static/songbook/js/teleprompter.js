/* teleprompter.js
   - Robust teleprompter scrolling (requestAnimationFrame)
   - Toggles chord diagrams
   - Swipe navigation between songs
   - Auto-hide overlay controls
   - Responsive lyrics container sizing
   - Scroll speed control (+ / - / Save)
   - Fully mobile / iPad Safari compatible
*/

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {

  // --- Device detection / debug ---
  const ua = navigator.userAgent;
  const isiPad = /iPad|Macintosh/i.test(ua) && navigator.maxTouchPoints > 1;
  const isiPhone = /iPhone/i.test(ua);
  console.log(`teleprompter.js loaded ✅`);
  console.log(`Device info: ${ua}`);
  if (isiPad) console.log("Detected iPad ✅");
  if (isiPhone) console.log("Detected iPhone ✅");  





    const $ = (sel, root = document) => root.querySelector(sel);

    // --- State ---
    let rafId = null;
    let lastRafTime = null;
    let isAutoScrolling = false;
    let scrollAccumulator = 0;
    let speedSetting = window.initialScrollSpeed || 40;

    // --- Speed range ---
    const SPEED_STEP = 5;
    const MIN_SPEED = 5;
    const MAX_SPEED = 300;

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

    // --- Layout ---
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

    // --- Scrolling Engine (iPad compatible) ---
    function stepScroll(ts) {
      if (!lastRafTime) lastRafTime = ts;
      const dt = (ts - lastRafTime) / 1000;
      lastRafTime = ts;
    
      const c = $(".lyrics-container");
      if (!c) return stopScroll();
    
      scrollAccumulator += pixelsPerSecond() * dt;
      const whole = Math.floor(scrollAccumulator);
    
      if (whole !== 0) {
        c.scrollBy(0, whole);
        scrollAccumulator -= whole;
      }
    
      // ✅ Safari-friendly tolerance for float rounding
      console.log("ScrollTop:", c.scrollTop);

      const reachedEnd = c.scrollTop + c.clientHeight >= c.scrollHeight - 5;
      if (reachedEnd) {
        console.log("🎵 Reached bottom, stopping scroll");
        return stopScroll();
      }
    
      rafId = requestAnimationFrame(stepScroll);
    }
    

    function startScroll() {
      if (isAutoScrolling) return;
      const c = $(".lyrics-container");
      if (!c || c.scrollHeight <= c.clientHeight) return;

      // iPad requires user gesture before scrolling
      if (!document.body.classList.contains("user-interacted")) {
        document.body.classList.add("user-interacted");
      }

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

    // --- Swipe Navigation ---
    let touchStartX = 0;
    document.addEventListener("touchstart", (e) => {
      touchStartX = e.touches[0].screenX;
      document.body.classList.add("user-interacted"); // allow iPad scrolling
    }, { passive: true });

    document.addEventListener("touchend", (e) => {
      const dx = e.changedTouches[0].screenX - touchStartX;
      if (dx < -50) {
        const rightLink = document.querySelector("#nav-overlay .right");
        if (rightLink) window.location.href = rightLink.href;
      }
      if (dx > 50) {
        const leftLink = document.querySelector("#nav-overlay .left");
        if (leftLink) window.location.href = leftLink.href;
      }
    }, { passive: true });

    // --- Overlay ---
    let overlayTimer = null;
    function showOverlay() {
      $("#nav-overlay")?.classList.remove("hidden");
      clearTimeout(overlayTimer);
      overlayTimer = setTimeout(() => $("#nav-overlay")?.classList.add("hidden"), 3000);
    }

    // --- Initialize UI ---
    $("#scroll-toggle")?.addEventListener("click", () => (isAutoScrolling ? stopScroll() : startScroll()));
    $("#scroll-reset")?.addEventListener("click", resetScroll);
    $("#toggle-chords")?.addEventListener("click", toggleChordSection);

    // --- Speed Controls ---
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
          saveBtn.textContent = "✅ Saved";
          setTimeout(() => (saveBtn.textContent = "💾 Save"), 1500);
        } catch (err) {
          console.error("⚠️ Error saving scroll speed:", err);
          alert("⚠️ Error saving scroll speed. Please try again.");
        }
      });
    }

    // --- Layout & interactions ---
    updateLyricsContainerHeight();
    window.addEventListener("resize", updateLyricsContainerHeight, { passive: true });
    window.addEventListener("orientationchange", () => setTimeout(updateLyricsContainerHeight, 200));

    bindPauseOnUserScroll($(".lyrics-container"));

    // --- Chords JSON load ---
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

    // --- Overlay ---
    if ($("#nav-overlay")) {
      showOverlay();
      ["mousemove", "touchstart", "click"].forEach((evt) =>
        document.addEventListener(evt, showOverlay, { passive: true })
      );
    }

  }); // <-- closes DOMContentLoaded
})(); // <-- closes IIFE
