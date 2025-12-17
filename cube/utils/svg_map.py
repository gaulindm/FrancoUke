# cube/utils/svg_map.py

# Standard facelet order:
# indices 0..8   = U face (row-major)
#        9..17  = R face
#       18..26  = F face
#       27..35  = D face
#       36..44  = L face
#       45..53  = B face

FACES = [('U', 0), ('R', 9), ('F', 18), ('D', 27), ('L', 36), ('B', 45)]

# Build mapping index -> svg element id like 'sticker-U-0-0' (row, col)
FACELET_TO_SVG_ID = {}
for face, start_idx in FACES:
    for i in range(9):
        idx = start_idx + i
        r, c = divmod(i, 3)
        FACELET_TO_SVG_ID[idx] = f"sticker-{face}-{r}-{c}"

# Color palette (standard)
COLOR_HEX = {
    "U": "#FFFFFF",   # white
    "R": "#D32F2F",   # red
    "F": "#2E7D32",   # green
    "D": "#FFEB3B",   # yellow
    "L": "#F57C00",   # orange
    "B": "#1565C0",   # blue
    "X": "#3b3b3b",   # ignore
}
