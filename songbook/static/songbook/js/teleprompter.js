/* teleprompter.js
   - Robust teleprompter scrolling (requestAnimationFrame)
   - Toggles chord diagrams
   - Swipe navigation between songs
   - Auto-hide overlay controls
   - Responsive lyrics container sizing
*/

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);

  // --- State ---
  let rafId = null;
  let lastRafTime = null;
  let isAutoScrolling = false;
  let speedSetting = 5;
  const SPEED_MULTIPLIER = 60; // px/sec per slider unit

  function pixelsPerSecond() {
    return Math.max(1, speedSetting) * SPEED_MULTIPLIER;
  }

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

  function stepScroll(ts) {
    if (!lastRafTime) lastRafTime = ts;
    const dt = (ts - lastRafTime) / 1000;
    lastRafTime = ts;

    const c = $(".lyrics-container");
    if (!c) return stopScroll();

    const delta = pixelsPerSecond() * dt;
    c.scrollTop = Math.min(c.scrollTop + delta, c.scrollHeight - c.clientHeight);

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
    $("#scroll-toggle")?.addEventListener("click", () => (isAutoScrolling ? stopScroll() : startScroll()));
    $("#scroll-reset")?.addEventListener("click", resetScroll);
    $("#scroll-speed")?.addEventListener("input", (e) => (speedSetting = +e.target.value));
    $("#toggle-chords")?.addEventListener("click", toggleChordSection);

    updateLyricsContainerHeight();
    window.addEventListener("resize", updateLyricsContainerHeight, { passive: true });
    window.addEventListener("orientationchange", () => setTimeout(updateLyricsContainerHeight, 200));

    bindPauseOnUserScroll($(".lyrics-container"));

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

    if ($("#nav-overlay")) {
      showOverlay();
      ["mousemove", "touchstart", "click"].forEach((evt) =>
        document.addEventListener(evt, showOverlay, { passive: true })
      );
    }
  });
})();
