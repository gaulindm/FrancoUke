export function renderCube(svgElement, cubeState) {

    const COLOR_MAP = {
        W: "#ffffff",
        Y: "#ffff00",
        R: "#ff0000",
        O: "#ff8000",
        B: "#0000ff",
        G: "#00cc00",
        X: "#CCCCCC",
    };

    const faces = ["U", "R", "F", "D", "L", "B"];

    // 🔑 Support BOTH old and new data shapes
    const cube = cubeState.cube ? cubeState.cube : cubeState;
    const highlights = cubeState.highlight?.stickers || [];

    function isHighlighted(face, r, c) {
        return highlights.some(
            ([f, row, col]) => f === face && row === r && col === c
        );
    }

    faces.forEach(face => {
        const grid = cube[face];
        if (!grid) return; // safety guard

        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 3; c++) {
                const stickerId = `sticker-${face}-${r}-${c}`;

                let sticker =
                    svgElement.getElementById(stickerId) ||
                    document.getElementById(stickerId);

                if (!sticker) continue;

                const rawColor = grid[r][c];
                const fillColor = COLOR_MAP[rawColor] || rawColor;

                sticker.setAttribute("fill", fillColor);

                // ✨ Highlight support
                if (isHighlighted(face, r, c)) {
                    sticker.setAttribute("stroke", "#ffcc00");
                    sticker.setAttribute("stroke-width", "3");
                    sticker.style.filter = "drop-shadow(0 0 6px #ffcc00)";
                } else {
                    sticker.setAttribute("stroke", "#000");
                    sticker.setAttribute("stroke-width", "1");
                    sticker.style.filter = "";
                }
            }
        }
    });
}
