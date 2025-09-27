/* teleprompter.js
   - Handles teleprompter scrolling
   - Toggles chord diagrams
   - Swipe navigation between songs
   - Auto-hide overlay controls
   - Uses chord_diagrams.js to render backend-provided chord shapes
*/

(function () {
  function $(sel, root = document) {
    return root.querySelector(sel);
  }

  // --- Auto Scroll ---
  let scrollInterval = null;
  let scrollSpeed = 5; // 1–10 from UI

  function startScroll() {
    if (scrollInterval) return; // already running
    const container = $(".lyrics-container");
    scrollInterval = setInterval(() => {
      container.scrollBy(0, 1);
      if (
        container.scrollTop + container.clientHeight >=
        container.scrollHeight
      ) {
        stopScroll(); // stop at bottom
      }
    }, 30 - scrollSpeed);
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

  // --- Chord Diagrams ---
  function renderChordDiagrams(chords) {
    const container = document.getElementById("chord-diagrams");
    container.innerHTML = "";

    const prefs = window.userPreferences || {};
    const showAlternate = prefs.showAlternate || false;

    chords.forEach((chord) => {
      if (!chord.variations || chord.variations.length === 0) {
        console.warn("⚠️ No variations for chord", chord.name);
        return;
      }

      // Only show first variation unless user wants all
      const variationsToRender = showAlternate
        ? chord.variations
        : [chord.variations[0]];

      variationsToRender.forEach((variation) => {
        const wrapper = document.createElement("div");
        wrapper.className = "chord-wrapper";
        wrapper.style.display = "inline-block";
        wrapper.style.margin = "0";

        if (typeof drawChordDiagram === "function") {
          drawChordDiagram(wrapper, {
            name: chord.name,
            ...variation,
          });
        } else {
          console.error("❌ drawChordDiagram is not defined!");
        }

        container.appendChild(wrapper);
      });
    });
  }

  function toggleChordSection() {
    const section = $("#chord-section");
    section.classList.toggle("hidden");

    const btn = $("#toggle-chords");
    btn.textContent = section.classList.contains("hidden")
      ? "Show Chords"
      : "Hide Chords";

    // (Re)draw chords when showing
    if (!section.classList.contains("hidden") && window.SONG?.chords) {
      renderChordDiagrams(window.SONG.chords);
    }
  }

  // --- Swipe detection for navigation ---
  let touchStartX = 0;
  let touchEndX = 0;

  function handleSwipe() {
    if (touchEndX < touchStartX - 50) {
      // Swipe left → next song
      const nextBtn = document.querySelector("#nav-overlay .right");
      if (nextBtn) window.location.href = nextBtn.href;
    }
    if (touchEndX > touchStartX + 50) {
      // Swipe right → prev song
      const prevBtn = document.querySelector("#nav-overlay .left");
      if (prevBtn) window.location.href = prevBtn.href;
    }
  }

  document.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
  });

  document.addEventListener("touchend", (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  });

  // --- Overlay auto-hide ---
  let overlayTimer = null;
  const overlay = $("#nav-overlay");

  function showOverlay() {
    if (!overlay) return;
    overlay.classList.remove("hidden");

    clearTimeout(overlayTimer);
    overlayTimer = setTimeout(() => {
      overlay.classList.add("hidden");
    }, 3000); // hide after 3s of inactivity
  }

  function resetOverlayTimer() {
    showOverlay();
  }

  // --- Init ---
  document.addEventListener("DOMContentLoaded", () => {
    // Scroll controls
    $("#scroll-toggle")?.addEventListener("click", () => {
      if (scrollInterval) stopScroll();
      else startScroll();
    });

    $("#scroll-reset")?.addEventListener("click", resetScroll);

    $("#scroll-speed")?.addEventListener("input", (e) => {
      scrollSpeed = parseInt(e.target.value, 10);
      if (scrollInterval) {
        stopScroll();
        startScroll(); // restart with new speed
      }
    });

    // Chords toggle
    $("#toggle-chords")?.addEventListener("click", toggleChordSection);

    // --- Load chords from <script id="chords-data"> ---
    const chordDataEl = document.getElementById("chords-data");
    if (chordDataEl) {
      try {
        const chords = JSON.parse(chordDataEl.textContent);
        console.log("✅ Parsed chords from template:", chords);

        if (Array.isArray(chords) && chords.length > 0) {
          renderChordDiagrams(chords);
        } else {
          console.warn("⚠️ No chords found in parsed JSON.");
        }
      } catch (err) {
        console.error("❌ Failed to parse chords JSON:", err);
      }
    } else {
      console.warn("⚠️ No <script id='chords-data'> element found.");
    }

    // Overlay auto-hide logic
    if (overlay) {
      // Show immediately on load
      showOverlay();

      // Reset timer on interactions
      ["mousemove", "touchstart", "click"].forEach((evt) => {
        document.addEventListener(evt, resetOverlayTimer);
      });
    }
  });
})();
