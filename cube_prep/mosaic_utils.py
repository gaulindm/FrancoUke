import json
from django.shortcuts import get_object_or_404
from .models import Mosaic


def load_mosaic_data(mosaic_id):
    mosaic = get_object_or_404(Mosaic, id=mosaic_id)

    rows = mosaic.cube_rows
    cols = mosaic.cube_cols

    cubes = [[None for _ in range(cols)] for _ in range(rows)]

    for mc in mosaic.mosaiccubes.select_related("cube"):
        cubes[mc.row][mc.col] = mc.cube.colors

    return mosaic, cubes
