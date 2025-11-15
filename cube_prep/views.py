from django.shortcuts import render
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import random, os
from reportlab.pdfgen import canvas
from cube_prep.cube_flowable import CubeFlowable



from .cube_flowable import CubeFlowable

# --- Sample move icons folder ---
MOVE_ICONS_DIR = os.path.join("cube_prep", "static", "cube_prep", "moves")

# --- Sample scrambles ---
PATTERNS = {
    "Face Solved": ["R U R' U'"],
    "Checkerboard": ["M2 E2 S2"],
    "Simple Scramble": ["R U R' U'", "L' U2 L", "U R U' R'"]
}

# --- View: Home page ---
def generator_home(request):
    return render(request, "cube_prep/generator.html")



def move_to_filename(move):
    """Convert move notation to PNG filename."""
    if move.endswith("'"):
        return move[0] + "_prime.png"   # e.g., R' -> R_prime.png
    else:
        return move + ".png"            # e.g., R2 -> R2.png, R -> R.png

def generate_two_cards_view(request):
    """
    Generate PDF with 2 horizontal cards per page:
    - Left: cube reference
    - Right: scramble icons only
    Only uses R, U, L, D moves for simplicity.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="two_horizontal_cube_cards.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    page_width, page_height = letter

    cube_size = 40
    margin = 20
    icon_size = 54  # triple previous 18x18
    MOVE_ICONS_DIR = "cube_prep/static/cube_prep/moves/"  # PNGs for moves

    # Horizontal layout offsets
    card_positions = [page_height - margin - cube_size*3, margin]  # top and bottom cards

    # Scramble moves (no B or F)
    PATTERNS = ["R", "U", "L", "D", "R'", "U'", "L'", "D'", "R2", "U2", "L2", "D2"]

    for y_offset in card_positions:

        # --- Left: Cube ---
        cube = CubeFlowable(size=cube_size)
        c.saveState()
        c.translate(margin, y_offset)
        cube.canv = c
        cube.draw()
        c.restoreState()

        # --- Right: Scramble icons only ---
        seq_moves = random.choices(PATTERNS, k=9)   # 9-move scramble
        icon_y = y_offset + cube_size*1.2  # start slightly above cube vertical center
        icon_x = margin + cube.width + 20

        for move in seq_moves:
            icon_file = move_to_filename(move)
            icon_path = f"{MOVE_ICONS_DIR}{icon_file}"
            try:
                c.drawImage(icon_path, icon_x, icon_y, width=icon_size, height=icon_size, preserveAspectRatio=True)
            except:
                pass
            icon_x += icon_size + 5  # horizontal spacing

        # Optional: horizontal line to separate cards
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(margin, y_offset-5, page_width - margin, y_offset-5)

    c.showPage()
    c.save()
    return response


def generate_three_cards_view(request):
    """
    Generate PDF with 3 vertical cards per page:
    - Left: cube reference
    - Right: scramble icons only
    Only uses R, U, L, D and F moves for simplicity.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="three_vertical_cube_cards.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    page_width, page_height = letter

    margin = 20
    icon_size = 40  # triple previous 18x18
    MOVE_ICONS_DIR = "cube_prep/static/cube_prep/moves/"  # PNGs for moves

    # Cube size: smaller to fit 3 cards
    cube_size = (page_height - 4*margin) / 3 * 0.15  # 15% of card height
    card_height = (page_height - 4*margin) / 3  # height per card

    # Vertical layout offsets for top, middle, bottom cards
    card_positions = [
        page_height - margin - card_height,        # top card
        page_height - 2*margin - 2*card_height,   # middle card
        margin                                     # bottom card
    ]

    # Scramble moves (no B or F)
    MOVES = ["R", "U", "L", "D", "R'", "U'", "L'", "D'", "R2", "U2", "L2", "D2","F","F'","F2"]

    for y_offset in card_positions:
        # --- Left: Cube ---
        cube = CubeFlowable(size=cube_size)
        c.saveState()
        vertical_shift = 0.1 * card_height  # shift cube slightly down in card
        c.translate(margin, y_offset + vertical_shift)
        cube.canv = c
        cube.draw()
        c.restoreState()

        # --- Right: Scramble icons ---
        seq_moves = random.choices(MOVES, k=9)  # 9-move scramble
        icon_x = margin + cube_size + 140
        icon_y = y_offset + cube_size*4  # adjust vertical start of icons

        for move in seq_moves:
            icon_file = move_to_filename(move)
            icon_path = os.path.join(MOVE_ICONS_DIR, icon_file)
            try:
                c.drawImage(icon_path, icon_x, icon_y, width=icon_size, height=icon_size, preserveAspectRatio=True)
            except:
                pass
            icon_x += icon_size + 5  # horizontal spacing

        # Optional: horizontal line to separate cards
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(margin, y_offset-5, page_width - margin, y_offset-5)

    c.showPage()
    c.save()
    return response

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Cube


def save_cube_colors(request):
    """Save the cube matrix JSON to the Cube model."""
    if request.method == "POST":
        colors_json = request.POST.get("colors_json")
        name = request.POST.get("name", "Unnamed Cube")

        cube = Cube.objects.create(name=name, colors=colors_json)
        return JsonResponse({"success": True, "cube_id": cube.id})

    return JsonResponse({"success": False, "error": "POST request required"})


from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

# If you eventually save cubes in the database:
# from .models import MosaicCube


def color_matrix_view(request):
    """Render the cube editor with a default of 1 cube per side."""
    cubes_per_side = int(request.GET.get("cubes", 1))
    rows = range(cubes_per_side * 3)
    cols = range(cubes_per_side * 3)
    return render(request, "cube_prep/color_matrix.html", {
        "cubes_per_side": cubes_per_side,
        "rows": rows,
        "cols": cols
    })



# OPTIONAL — If you want a second URL or future features:
def color_cube_view(request):
    """
    Legacy / alternate URL pointing to the same tool.
    """

    size = 3  # Keep consistent
    return render(request, "cube_prep/color_matrix.html", {
        "size": size,
        "rows": range(size),
        "cols": range(size),
    })

import json
from django.http import JsonResponse
from .models import Cube, Mosaic

from django.shortcuts import render
from django.http import JsonResponse
from .models import Cube, Mosaic
import json

def color_mosaic_view(request):
    """Render the mosaic editor page."""
    return render(request, "cube_prep/color_mosaic.html")

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Cube, Mosaic

@csrf_exempt
def save_mosaic(request):
    if request.method == "POST":
        try:
            mosaic_json = request.POST.get("mosaic_json")
            mosaic_name = request.POST.get("mosaic_name", "Untitled Mosaic")

            mosaic_data = json.loads(mosaic_json)
            mosaic_size = int(len(mosaic_data) ** 0.5)  # cube grid = √num_cubes

            mosaic = Mosaic.objects.create(name=mosaic_name)

            letters = "abcdefghijklmnopqrstuvwxyz"

            for index, cube_data in enumerate(mosaic_data):

                row = index // mosaic_size        # 0,1,2...
                col = index % mosaic_size         # 0,1,2...

                suffix = f"{row+1}{letters[col]}"  # 1a, 1b, 1c...

                cube = Cube.objects.create(
                    name=f"{mosaic_name}-{suffix}",
                    colors=json.dumps(cube_data)
                )

                mosaic.cubes.add(cube)

            return JsonResponse({"success": True, "mosaic_id": mosaic.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "POST request required"})
