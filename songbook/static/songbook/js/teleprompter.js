/* teleprompter.js
   - Handles teleprompter scrolling
   - Toggles chord diagrams
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
  const container = $("#chord-diagrams");
  if (!container) {
    console.error("❌ #chord-diagrams not found in DOM");
    return;
  }
  container.innerHTML = "";

  chords.forEach((chord) => {
    if (!chord.variations || chord.variations.length === 0) {
      console.warn("⚠️ No variations for chord", chord.name);
      return;
    }

    chord.variations.forEach((variation, idx) => {
      const wrapper = document.createElement("div");
      wrapper.className = "chord-wrapper";
      wrapper.style.display = "inline-block";
      wrapper.style.margin = "10px";

      //const label = document.createElement("div");
      //label.textContent =
      //  chord.name + (chord.variations.length > 1 ? ` (v${idx + 1})` : "");
      //label.style.textAlign = "center";
      //label.style.marginBottom = "4px";
      //wrapper.appendChild(label);

      container.appendChild(wrapper);

      drawChordDiagram(wrapper, {
        name: chord.name,
        ...variation,
      });
    });
  });
}


  function toggleChordSection() {
    const section = $("#chord-section");
    const isHidden = section.style.display === "none";
    section.style.display = isHidden ? "block" : "none";

    // (Re)draw chords when showing the section
    if (isHidden && window.SONG && Array.isArray(window.SONG.chords)) {
      renderChordDiagrams(window.SONG.chords);
    }
  }
// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
  // Scroll controls
  $("#scroll-toggle").addEventListener("click", () => {
    if (scrollInterval) stopScroll();
    else startScroll();
  });

  $("#scroll-reset").addEventListener("click", resetScroll);

  $("#scroll-speed").addEventListener("input", (e) => {
    scrollSpeed = parseInt(e.target.value, 10);
    if (scrollInterval) {
      stopScroll();
      startScroll(); // restart with new speed
    }
  });

  // Chords toggle
  $("#toggle-chords").addEventListener("click", toggleChordSection);

  // --- Load chords from <script id="chords-data"> ---
  const chordDataEl = document.getElementById("chords-data");
  if (chordDataEl) {
    try {
      const chords = JSON.parse(chordDataEl.textContent);
      console.log("✅ Parsed chords from template:", chords);  // DEBUG LOG

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
});


})();
