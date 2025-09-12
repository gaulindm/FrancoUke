// assets/static/assets/js/asset_chooser.js
document.addEventListener("DOMContentLoaded", function () {
  // Single asset chooser (existing)
  document.querySelectorAll(".asset-chooser-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const inputId = btn.dataset.inputId;
      const win = window.open(
        "/admin/assets/chooser_modal/?multi=0",
        "Choose Asset",
        "width=900,height=700"
      );
      win.selectedCallback = function (asset) {
        const input = document.getElementById(inputId);
        input.value = asset.id;

        // replace or create preview
        let preview = input.parentNode.querySelector(".asset-preview");
        if (!preview) {
          preview = document.createElement("div");
          preview.classList.add("asset-preview");
          input.parentNode.appendChild(preview);
        }
        preview.innerHTML = `<img src="${asset.thumb}" style="max-width:150px;max-height:100px">`;
      };
    });
  });

  // Gallery multi chooser
  document.querySelectorAll(".asset-gallery-chooser-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const inputName = btn.dataset.inputName; // e.g. "gallery_assets"
      // find an existing hidden inputs container (we render hidden inputs in widget)
      const container = btn.closest(".asset-gallery-widget");
      const win = window.open(
        "/admin/assets/chooser_modal/?multi=1",
        "Choose Gallery Assets",
        "width=1000,height=800"
      );

      win.selectedCallback = function (assets) {
        // assets is an array of asset objects
        // Remove any existing hidden inputs for this field
        const existing = container.querySelectorAll(`input[name="${inputName}"]`);
        existing.forEach(e => e.remove());

        // Add new hidden inputs for each selected asset id
        assets.forEach(a => {
          const inp = document.createElement("input");
          inp.type = "hidden";
          inp.name = inputName;
          inp.value = a.id;
          inp.className = "asset-gallery-hidden";
          container.insertBefore(inp, btn); // put before the button
        });

        // Update preview area
        const preview = container.querySelector(".gallery-preview");
        preview.innerHTML = "";
        assets.forEach(a => {
          const img = document.createElement("img");
          img.src = a.thumb;
          img.style = "max-width:100px;max-height:80px;margin:2px;border-radius:4px;";
          preview.appendChild(img);
        });
      };
    });
  });
});

  