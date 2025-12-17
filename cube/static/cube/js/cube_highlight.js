// cube/js/cube_highlight.js

export function applyHighlights(svg, highlight) {
    const { edges = [], style = {} } = highlight;

    edges.forEach(({ face, row, col }) => {
        const id = `face-${face}-${row}-${col}`;
        const cell = svg.getElementById(id);
        if (!cell) return;

        cell.style.stroke = style.stroke || "#FFD700";
        cell.style.strokeWidth = style.strokeWidth || 3;

        if (style.glow) {
            cell.style.filter = "drop-shadow(0 0 6px rgba(255,215,0,0.9))";
        }
    });
}
