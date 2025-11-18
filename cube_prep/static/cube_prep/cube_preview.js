/**
 * Draw a simple isometric cube preview on a canvas
 * @param {HTMLCanvasElement} canvas 
 * @param {string} topColor - color of the Up face (W/R/B/G/O/Y)
 * @param {string} frontColor - color of the Front face
 */
function drawCubeFlowable(canvas, topColor, frontColor) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Map cube letters to CSS colors
    const colorMap = {
        "W": "#FFFFFF",
        "R": "#FF0000",
        "B": "#0000FF",
        "G": "#00AA00",
        "O": "#FF8800",
        "Y": "#FFFF00"
    };

    const top = colorMap[topColor] || "#CCCCCC";
    const front = colorMap[frontColor] || "#888888";
    const right = "#CCCCCC"; // default right face color

    // Cube dimensions
    const size = Math.min(width, height) * 0.6;
    const skew = size * 0.25;
    const offsetX = (width - size - skew) / 2;
    const offsetY = (height - size - skew) / 2;

    // --------------------
    // Draw FRONT FACE (vertical squares)
    // --------------------
    ctx.beginPath();
    ctx.moveTo(offsetX, offsetY + skew);
    ctx.lineTo(offsetX + size, offsetY + skew);
    ctx.lineTo(offsetX + size, offsetY + size + skew);
    ctx.lineTo(offsetX, offsetY + size + skew);
    ctx.closePath();
    ctx.fillStyle = front;
    ctx.fill();
    ctx.stroke();

    // --------------------
    // Draw RIGHT FACE (parallelogram to the right)
    // --------------------
    ctx.beginPath();
    ctx.moveTo(offsetX + size, offsetY + skew);
    ctx.lineTo(offsetX + size + skew, offsetY);
    ctx.lineTo(offsetX + size + skew, offsetY + size);
    ctx.lineTo(offsetX + size, offsetY + size + skew);
    ctx.closePath();
    ctx.fillStyle = right;
    ctx.fill();
    ctx.stroke();

    // --------------------
    // Draw TOP FACE (parallelogram up)
    // --------------------
    ctx.beginPath();
    ctx.moveTo(offsetX, offsetY + skew);
    ctx.lineTo(offsetX + skew, offsetY);
    ctx.lineTo(offsetX + size + skew, offsetY);
    ctx.lineTo(offsetX + size, offsetY + skew);
    ctx.closePath();
    ctx.fillStyle = top;
    ctx.fill();
    ctx.stroke();
}
