# utilities.py

import random
from django.shortcuts import get_object_or_404
from reportlab.platypus import Image

from .models import Mosaic

ALLOWED_MOVES = [
    "U", "U'", "U2",
    "D", "D'", "D2",
    "L", "L'", "L2",
    "R", "R'", "R2",
]

def load_mosaic_data(mosaic_id):
    mosaic = get_object_or_404(Mosaic, id=mosaic_id)
    rows = mosaic.cube_rows
    cols = mosaic.cube_cols

    cubes = [[None for _ in range(cols)] for _ in range(rows)]

    for cube in mosaic.cubes.all():
        squares = cube.squares.order_by("square_index")
        colors = [sq.color for sq in squares]
        cubes[cube.cube_row][cube.cube_col] = colors

    return mosaic, cubes


def generate_simple_scramble():
    result = []
    last_face = None

    for _ in range(12):
        move = random.choice(ALLOWED_MOVES)

        while last_face and move[0] == last_face:
            move = random.choice(ALLOWED_MOVES)

        result.append(move)
        last_face = move[0]

    return result


def build_icon_images(scramble_moves, size=45):
    icons = []
    for move in scramble_moves:
        path = f"cube_icons/{move}.png"  # You ensured these exist
        icons.append(Image(path, width=size, height=size))
    return icons
