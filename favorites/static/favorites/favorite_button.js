/* favorites/static/favorites/favorite_button.js
   Shared by the chord sheet and the teleprompter. Looks for <button id="favorite-btn">:
     data-url   = where to POST the toggle
     data-csrf  = the CSRF token
   Optional inside it:
     #favorite-icon  - either a Bootstrap Icon (<i class="bi bi-heart">), or a glyph
                       element carrying data-icon-on / data-icon-off (e.g. ♥ / ♡)
     #favorite-count - leaders' count, updated when the server sends one
   The server answers {is_favorite: true/false, count: n or null}. */
   (function () {
    var btn = document.getElementById("favorite-btn");
    if (!btn) return;
    var icon  = document.getElementById("favorite-icon");
    var count = document.getElementById("favorite-count");
  
    function showState(isFavorite) {
      btn.setAttribute("aria-pressed", isFavorite ? "true" : "false");
      btn.classList.toggle("is-favorite", isFavorite);
      if (!icon) return;
      if (icon.dataset.iconOn) {                       // glyph style (teleprompter)
        icon.textContent = isFavorite ? icon.dataset.iconOn : icon.dataset.iconOff;
      } else {                                         // Bootstrap Icons style (chord sheet)
        icon.classList.toggle("bi-heart-fill", isFavorite);
        icon.classList.toggle("bi-heart", !isFavorite);
      }
    }
  
    btn.addEventListener("click", async function () {
      if (btn.disabled) return;
      btn.disabled = true;                             // ignore double taps while saving
      try {
        var response = await fetch(btn.dataset.url, {
          method: "POST",
          headers: { "X-CSRFToken": btn.dataset.csrf, "X-Requested-With": "XMLHttpRequest" },
          credentials: "same-origin"
        });
        if (!response.ok) throw new Error("HTTP " + response.status);
        var data = await response.json();
        showState(!!data.is_favorite);
        if (count && typeof data.count === "number") { count.textContent = data.count; }
      } catch (err) {
        console.error("Could not save favorite:", err);   // heart stays as it was
      } finally {
        btn.disabled = false;
      }
    });
  })();