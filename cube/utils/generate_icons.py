import os
from cube.utils.svggen import svg_icon

MOVES = ["U","U'","U2","R","R'","R2","F","F'","F2","L","L'","L2",
         "D","D'","D2"]

def generate_all():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "static", "cube", "icons")
    os.makedirs(output_dir, exist_ok=True)

    for move in MOVES:
        svg = svg_icon(move)
        with open(os.path.join(output_dir, f"{move}.svg"), "w") as f:
            f.write(svg)

    print("✔ All SVG icons generated!")


if __name__ == "__main__":
    generate_all()
