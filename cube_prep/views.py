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
from reportlab.lib import colors as rl_colors

from .models import Cube, Mosaic
from .cube_flowable import CubeFlowable
from .cube_utils import generate_face_moves

from reportlab.lib import colors

CUBE_COLOR_MAP = {
    "W": rl_colors.white,
    "R": rl_colors.red,
    "B": rl_colors.blue,
    "G": rl_colors.green,
    "O": rl_colors.orange,
    "Y": rl_colors.yellow,
    "": rl_colors.HexColor("#CCCCCC")  # fallback gray
}


# --- Constants ---
MOVE_ICONS_DIR = os.path.join("cube_prep", "static", "cube_prep", "moves")
PATTERNS = {
    "Face Solved": ["R U R' U'"],
    "Checkerboard": ["M2 E2 S2"],
    "Simple Scramble": ["R U R' U'", "L' U2 L", "U R U' R'"]
}


# --- Views ---

def generator_home(request):
    cubes = Cube.objects.all().order_by('name')  # all cubes for dropdown
    return render(request, "cube_prep/generator.html", {"cubes": cubes})



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

def generate_three_copies_pdf(request):
    cube_id = request.GET.get("cube_id")
    if not cube_id:
        return HttpResponse("Cube ID missing", status=400)

    try:
        cube = Cube.objects.get(id=cube_id)
    except Cube.DoesNotExist:
        return HttpResponse("Cube not found", status=404)

    # --- Load moves dict ---
    moves_data = cube.moves if cube.moves else {}
    if isinstance(moves_data, dict):
        moves = {
            "up": moves_data.get("up", "W"),
            "front": moves_data.get("front", "R"),
            "sequence": moves_data.get("sequence", [])
        }
    else:
        moves = {"up": "W", "front": "R", "sequence": []}

    # --- Precompute icon filenames ---
    icon_moves = []
    for m in moves["sequence"]:
        if "'" in m:
            icon_moves.append(m.replace("'", "_prime"))
        else:
            icon_moves.append(m)

    # --- PDF setup ---
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="three_copies_cube.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    page_width, page_height = letter
    margin = 20
    cube_size = (page_height - 4 * margin) / 3 * 0.15
    card_height = (page_height - 4 * margin) / 3
    icon_size = 40

    card_positions = [
        page_height - margin - card_height,
        page_height - 2 * margin - 2 * card_height,
        margin
    ]

    for y_offset in card_positions:
        # --- CubeFlowable with sanitized colors ---
        cube_flow = CubeFlowable(
            size=cube_size,
            front_color=CUBE_COLOR_MAP.get(moves["front"], colors.white),
            top_color=CUBE_COLOR_MAP.get(moves["up"], colors.white),
            right_color=colors.HexColor("#CCCCCC")
        )
        c.saveState()
        c.translate(margin, y_offset + 0.1 * card_height)
        cube_flow.canv = c
        cube_flow.draw()
        c.restoreState()

        # --- Draw move icons ---
        icon_x = margin + cube_size + 140
        icon_y = y_offset + cube_size * 4
        for move_file in icon_moves:
            icon_path = os.path.join(MOVE_ICONS_DIR, move_file + ".png")
            try:
                c.drawImage(icon_path, icon_x, icon_y, width=icon_size, height=icon_size, preserveAspectRatio=True)
            except:
                pass
            icon_x += icon_size + 5

        # --- Horizontal line under card ---
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(margin, y_offset - 5, page_width - margin, y_offset - 5)

    c.showPage()
    c.save()
    return response

def pdf_generator_view(request):
    cube_id = request.GET.get("cube_id")
    cube = None
    moves = {}
    icon_moves = []

    if cube_id:
        try:
            cube = Cube.objects.get(id=cube_id)

            # Cube.moves is ALREADY A DICT — do NOT json.loads()
            moves_data = cube.moves if cube.moves else {}

            # Normalize
            if isinstance(moves_data, dict):
                moves = {
                    "up": moves_data.get("up", "W"),
                    "front": moves_data.get("front", "R"),
                    "sequence": moves_data.get("sequence", [])
                }
            else:
                moves = {"up": "W", "front": "R", "sequence": []}

            # Pre-compute icon file names
            for move in moves["sequence"]:
                if "'" in move:
                    icon_moves.append(move.replace("'", "_prime"))
                else:
                    icon_moves.append(move)

        except Cube.DoesNotExist:
            cube = None
            moves = {}
            icon_moves = []

    cubes = Cube.objects.all().order_by("name")

    return render(request, "cube_prep/pdf_generator.html", {
        "cubes": cubes,
        "selected_cube": cube,
        "moves": moves,
        "icon_moves": icon_moves,
    })
