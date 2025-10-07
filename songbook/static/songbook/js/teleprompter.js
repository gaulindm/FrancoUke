/* teleprompter.js
   - Handles teleprompter scrolling
   - Toggles chord diagrams
   - Swipe navigation between songs
   - Auto-hide overlay controls
   - Uses chord_diagrams.js to render backend-provided chord shapes
   - Loads scroll speed & user preferences from <script id="teleprompter-config">
*/

(function () {
  function $(sel, root = document) {
    return root.querySelector(sel);
  }

  // --- Config & State ---
  let scrollInterval = null;
  let scrollSpeed = 20; // default pixels/sec equivalent
  const MIN_SPEED = 5;
  const MAX_SPEED = 300;
  const STEP = 5;

  function loadConfig() {
    const configEl = document.getElementById("teleprompter-config");
    if (!configEl) return console.warn("⚠️ No teleprompter config found.");
    try {
      const config = JSON.parse(configEl.textContent);
      window.userPreferences = config.userPreferences || {};
      scrollSpeed = parseInt(config.initialScrollSpeed, 10) || 20;
      console.log("✅ Loaded teleprompter config:", config);
    } catch (e) {
      console.error("❌ Failed to parse teleprompter config:", e);
    }
  }

  // --- Auto Scroll ---
  function startScroll() {
    if (scrollInterval) return;
    const container = $(".lyrics-container");
    scrollInterval = setInterval(() => {
      container.scrollBy(0, scrollSpeed / 30); // smooth ~30fps
      if (container.scrollTop + container.clientHeight >= container.scrollHeight)
        stopScroll();
    }, 30);

    $("#scroll-toggle").textContent = "⏸ Pause";
  }

  function stopScroll() {
    clearInterval(scrollInterval);
    scrollInterval = null;
    $("#scroll-toggle").textContent = "▶️ Start";
  }

  function resetScroll() {
    stopScroll();
    $(".lyrics-container").scrollTo({ top: 0, behavior: "smooth" });
  }

  // --- Chord rendering ---
  function renderChordDiagrams(chords) {
    const container = $("#chord-diagrams");
    if (!container) return;
    container.innerHTML = "";

    const prefs = window.userPreferences || {};
    const showAlternate = prefs.showAlternate || false;

    chords.forEach((chord) => {
      const variations = showAlternate ? chord.variations : [chord.variations[0]];
      variations.forEach((v) => {
        const wrap = document.createElement("div");
        wrap.className = "chord-wrapper";
        if (typeof drawChordDiagram === "function")
          drawChordDiagram(wrap, { name: chord.name, ...v });
        container.appendChild(wrap);
      });
    });
  }

  function toggleChordSection() {
    const section = $("#chord-section");
    section.classList.toggle("hidden");
    $("#toggle-chords").textContent = section.classList.contains("hidden")
      ? "Show Chords"
      : "Hide Chords";
    if (!section.classList.contains("hidden") && window.SONG?.chords)
      renderChordDiagrams(window.SONG.chords);
  }

  // --- Swipe Navigation ---
  let touchStartX = 0;
  document.addEventListener("touchstart", (e) => (touchStartX = e.touches[0].screenX));
  document.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].screenX - touchStartX;
    if (dx < -50) $("#nav-overlay .right")?.click();
    if (dx > 50) $("#nav-overlay .left")?.click();
  });

  // --- Overlay ---
  let overlayTimer = null;
  function showOverlay() {
    $("#nav-overlay")?.classList.remove("hidden");
    clearTimeout(overlayTimer);
    overlayTimer = setTimeout(() => $("#nav-overlay")?.classList.add("hidden"), 3000);
  }

  // --- Init ---
  document.addEventListener("DOMContentLoaded", () => {
    loadConfig();

    // Scroll buttons
    $("#scroll-toggle")?.addEventListener("click", () => {
      if (scrollInterval) stopScroll();
      else startScroll();
    });

    $("#scroll-reset")?.addEventListener("click", resetScroll);

    // --- Speed controls (− / +) ---
    const disp = $("#speed-display");
    const updateDisplay = () => {
      if (disp) disp.textContent = Math.round(scrollSpeed);
    };

    $("#speed-decrease")?.addEventListener("click", () => {
      scrollSpeed = Math.max(MIN_SPEED, scrollSpeed - STEP);
      updateDisplay();
    });

    $("#speed-increase")?.addEventListener("click", () => {
      scrollSpeed = Math.min(MAX_SPEED, scrollSpeed + STEP);
      updateDisplay();
    });

    updateDisplay();

    // Chords toggle
    $("#toggle-chords")?.addEventListener("click", toggleChordSection);

    // Chord data
    const chordsEl = document.getElementById("chords-data");
    if (chordsEl) {
      try {
        const chords = JSON.parse(chordsEl.textContent);
        if (Array.isArray(chords) && chords.length > 0)
          renderChordDiagrams(chords);
      } catch (e) {
        console.error("❌ Error parsing chords JSON:", e);
      }
    }

    // Overlay handling
    showOverlay();
    ["mousemove", "touchstart", "click"].forEach((evt) =>
      document.addEventListener(evt, showOverlay, { passive: true })
    );
  });
})();
