document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".asset-chooser-btn").forEach(btn => {
      btn.addEventListener("click", function () {
        const inputId = btn.dataset.inputId;
        const win = window.open(
          "/admin/assets/chooser_modal/",
          "Choose Asset",
          "width=800,height=600"
        );
        win.selectedCallback = function (asset) {
          const input = document.getElementById(inputId);
          input.value = asset.id;
          // optionally update preview
          const preview = document.createElement("div");
          preview.innerHTML = `<img src="${asset.thumb}" style="max-width:150px;max-height:100px">`;
          input.parentNode.appendChild(preview);
        };
      });
    });
  });
  