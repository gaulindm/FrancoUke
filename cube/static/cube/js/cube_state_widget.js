document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-widget]").forEach(initCubeWidget);
});

function initCubeWidget(widget) {
    const textarea = widget.querySelector("textarea");
    let state = JSON.parse(textarea.value);

    let selectedColor = "W";

    widget.querySelectorAll(".cube-color").forEach(btn => {
        btn.addEventListener("click", () => {
            selectedColor = btn.dataset.color;
        });
    });

    widget.querySelectorAll(".cube-face").forEach(faceEl => {
        const face = faceEl.dataset.face;
        const grid = faceEl.querySelector(".cube-grid");

        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 3; c++) {
                const cell = document.createElement("div");
                cell.className = "cube-cell";
                cell.dataset.face = face;
                cell.dataset.row = r;
                cell.dataset.col = c;
                cell.style.background = colorMap[state[face][r][c]];

                cell.addEventListener("click", () => {
                    state[face][r][c] = selectedColor;
                    cell.style.background = colorMap[selectedColor];
                    textarea.value = JSON.stringify(state);
                });

                grid.appendChild(cell);
            }
        }
    });
}

const colorMap = {
    W: "#fff",
    Y: "#ff0",
    G: "#0f0",
    B: "#00f",
    R: "#f00",
    O: "#f80",
    X: "#ccc"
};
