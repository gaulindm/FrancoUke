# views.py

import os
import random
import json
from io import BytesIO

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .models import Cube, Mosaic
from .cube_flowable import CubeFlowable
from .cube_utils import generate_face_moves


# --- Constants ---
MOVE_ICONS_DIR = os.path.join("cube_prep", "static", "cube_prep", "moves")
PATTERNS = {
    "Face Solved": ["R U R' U'"],
    "Checkerboard": ["M2 E2 S2"],
    "Simple Scramble": ["R U R' U'", "L' U2 L", "U R U' R'"]
}


# --- Views ---

def generator_home(request):
    """Render the cube generator home page."""
    return render(request, "cube_prep/generator.html")


def move_to_filename(move):
    """Convert move notation to PNG filename."""
    if move.endswith("'"):
        return move[0] + "_prime.png"
    else:
        return move + ".png"


def generate_three_cards_view(request):
    """Generate PDF with 3 vertical cube cards per page."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="three_vertical_cube_cards.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    page_width, page_height = letter
    margin = 20
    icon_size = 40
    cube_size = (page_height - 4*margin) / 3 * 0.15
    card_height = (page_height - 4*margin) / 3

    card_positions = [
        page_height - margin - card_height,
        page_height - 2*margin - 2*card_height,
        margin
    ]

    MOVES = ["R", "U", "L", "D", "R'", "U'", "L'", "D'", "R2", "U2", "L2", "D2", "F", "F'", "F2"]

    for y_offset in card_positions:
        cube = CubeFlowable(size=cube_size)
        c.saveState()
        vertical_shift = 0.1 * card_height
        c.translate(margin, y_offset + vertical_shift)
        cube.canv = c
        cube.draw()
        c.restoreState()

        seq_moves = random.choices(MOVES, k=9)
        icon_x = margin + cube_size + 140
        icon_y = y_offset + cube_size*4

        for move in seq_moves:
            icon_file = move_to_filename(move)
            icon_path = os.path.join(MOVE_ICONS_DIR, icon_file)
            try:
                c.drawImage(icon_path, icon_x, icon_y, width=icon_size, height=icon_size, preserveAspectRatio=True)
            except:
                pass
            icon_x += icon_size + 5

        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(margin, y_offset-5, page_width - margin, y_offset-5)

    c.showPage()
    c.save()
    return response


def save_cube_colors(request):
    """Save a single cube to the database."""
    if request.method == "POST":
        colors_json = request.POST.get("colors_json")
        name = request.POST.get("name", "Unnamed Cube")
        cube = Cube.objects.create(name=name, colors=colors_json)
        return JsonResponse({"success": True, "cube_id": cube.id})

    return JsonResponse({"success": False, "error": "POST request required"})


def color_matrix_view(request):
    """Render the cube editor with default 1 cube per side."""
    cubes_per_side = int(request.GET.get("cubes", 1))
    rows = range(cubes_per_side * 3)
    cols = range(cubes_per_side * 3)
    return render(request, "cube_prep/color_matrix.html", {
        "cubes_per_side": cubes_per_side,
        "rows": rows,
        "cols": cols
    })


def color_cube_view(request):
    """Legacy / alternate URL pointing to the same cube editor."""
    size = 3
    return render(request, "cube_prep/color_matrix.html", {
        "size": size,
        "rows": range(size),
        "cols": range(size),
    })


def color_mosaic_view(request):
    """Render the mosaic editor page."""
    return render(request, "cube_prep/color_mosaic.html")

@csrf_exempt
def save_mosaic(request):
    if request.method == "POST":
        try:
            mosaic_json = request.POST.get("mosaic_json")
            mosaic_name = request.POST.get("mosaic_name", "Untitled Mosaic")
            mosaic_data = json.loads(mosaic_json)
            mosaic_size = int(len(mosaic_data) ** 0.5)

            mosaic = Mosaic.objects.create(name=mosaic_name)
            letters = "abcdefghijklmnopqrstuvwxyz"

            for index, cube_data in enumerate(mosaic_data):
                row = index // mosaic_size
                col = index % mosaic_size
                suffix = f"{row+1}{letters[col]}"

                # Generate human-readable moves for this cube face
                moves_info = generate_face_moves(cube_data)

                cube = Cube.objects.create(
                    name=f"{mosaic_name}-{suffix}",
                    colors=json.dumps(cube_data),
                    moves=json.dumps(moves_info)   # store as JSON
                )
                mosaic.cubes.add(cube)

            return JsonResponse({"success": True, "mosaic_id": mosaic.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "POST request required"})


@csrf_exempt
def cube_face_moves_view(request):
    """
    Receives POST JSON of one cube face,
    returns minimal moves to reproduce it.
    """
    if request.method == "POST":
        try:
            target_face_json = request.POST.get("cube_face")
            target_face = json.loads(target_face_json)

            move_sequence = generate_face_moves(target_face)

            return JsonResponse({
                "success": True,
                "sequence": move_sequence
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "POST request required"})

