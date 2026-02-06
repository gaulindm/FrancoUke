import json
from django.shortcuts import get_object_or_404
from .models import Mosaic


def load_mosaic_grid(mosaic_id):
    """
    Returns:
        mosaic: Mosaic instance
        grid: 2D list [row][col] → cube colors (or None)
    """
    mosaic = get_object_or_404(Mosaic, id=mosaic_id)

    rows = mosaic.cube_rows
    cols = mosaic.cube_cols

    grid = [[None for _ in range(cols)] for _ in range(rows)]

    for cube in mosaic.cubes.all():
        try:
            colors = json.loads(cube.colors)
        except (TypeError, json.JSONDecodeError):
            colors = None

        grid[cube.cube_row][cube.cube_col] = colors

    return mosaic, grid
