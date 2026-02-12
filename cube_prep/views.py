# views.py - VERSION CORRIGÉE

import os
import random
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from io import BytesIO
from .models import Cube, Mosaic, MosaicCube
from django.http import HttpResponse
from .models import Mosaic
from .pdf_generator import generate_teacher_pdf


# --- Views ---

def generator_home(request):
    cubes = Cube.objects.all().order_by('name')  # all cubes for dropdown
    return render(request, "cube_prep/generator.html", {"cubes": cubes})


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

    print("\n" + "="*70)
    print("SAVE_MOSAIC CALLED")
    print("Method:", request.method)
    print("POST data:", request.POST)
    print("="*70)

    if request.method != 'POST':
        print("❌ Not POST")
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    try:
        mosaic_id = request.POST.get('mosaic_id')
        mosaic_name = request.POST.get('mosaic_name')
        cubes_per_side = request.POST.get('cubes_per_side')
        mosaic_json = request.POST.get('mosaic_json')

        print("Received mosaic_id:", mosaic_id)
        print("Received mosaic_name:", mosaic_name)
        print("Received cubes_per_side:", cubes_per_side)

        if not mosaic_json:
            print("❌ No mosaic_json")
            return JsonResponse({'success': False, 'error': 'No mosaic data provided'})

        cubes_data = json.loads(mosaic_json)
        print("Total cubes received:", len(cubes_data))

        # ----------------------------
        # UPDATE EXISTING
        # ----------------------------
        if mosaic_id:
            print("➡ UPDATE MODE")

            mosaic = Mosaic.objects.get(id=mosaic_id)
            print("Updating mosaic:", mosaic.id, mosaic.name)

            mosaic.name = mosaic_name
            mosaic.save()

            # DELETE OLD CUBES
            deleted_count = mosaic.mosaiccubes.count()
            print("Deleting", deleted_count, "old cubes")
            mosaic.mosaiccubes.all().delete()

        # ----------------------------
        # CREATE NEW
        # ----------------------------
        else:
            print("➡ CREATE MODE")
            mosaic = Mosaic.objects.create(name=mosaic_name)
            print("Created mosaic:", mosaic.id)

        cols = int(cubes_per_side)
        total = len(cubes_data)
        rows = total // cols

        print("Grid detected:", rows, "x", cols)

        created_count = 0

        for idx, cube_colors in enumerate(cubes_data):
            row = idx // cols
            col = idx % cols

            cube = Cube.objects.create(
                name=f"{mosaic_name}-{row}-{col}",
                colors=cube_colors
            )

            MosaicCube.objects.create(
                mosaic=mosaic,
                row=row,
                col=col,
                cube=cube
            )

            created_count += 1

        print("Created", created_count, "new cubes")
        print("FINAL mosaic ID:", mosaic.id)
        print("="*70 + "\n")

        return JsonResponse({
            'success': True,
            'mosaic_id': mosaic.id
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def mosaic_list(request):
    """Return list of all mosaics."""
    try:
        mosaics = Mosaic.objects.all().order_by("-created_at")

        return JsonResponse([
            {
                "id": m.id,
                "name": m.name,
                "created_at": m.created_at.isoformat() if hasattr(m, 'created_at') else None,
            }
            for m in mosaics
        ], safe=False)
    except Exception as e:
        print(f"ERROR in mosaic_list: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def mosaic_detail(request, mosaic_id):
    """Return details of a specific mosaic."""
    try:
        mosaic = Mosaic.objects.get(id=mosaic_id)

        cubes = []
        for mc in mosaic.mosaiccubes.all().order_by("row", "col"):
            cubes.append(mc.cube.colors)

        return JsonResponse({
            "id": mosaic.id,
            "name": mosaic.name,
            "cubes_per_side": mosaic.cube_cols,
            "cubes": cubes,
        })
    except Mosaic.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mosaic not found'
        }, status=404)
    except Exception as e:
        print(f"ERROR in mosaic_detail: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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

from reportlab.graphics.shapes import Drawing, Rect


def draw_cube_face(cube, size=70):
    """
    Draws a real 3x3 cube face from cube.colors JSON.
    """
    square_size = size / 3
    d = Drawing(size, size)

    for row in range(3):
        for col in range(3):
            color_letter = cube.colors[row][col]
            fill = COLOR_MAP.get(color_letter, rl_colors.grey)

            x = col * square_size
            y = size - (row + 1) * square_size

            square = Rect(
                x,
                y,
                square_size,
                square_size,
                fillColor=fill,
                strokeColor=rl_colors.black
            )
            d.add(square)

    return d


@csrf_exempt
def teacher_pdf(request):
    """
    Generate PDF for a mosaic.
    Accepts both GET and POST with mosaic_id parameter.
    """
    print("\n" + "="*70)
    print("TEACHER_PDF CALLED")
    print("Method:", request.method)
    print("GET params:", request.GET)
    print("POST params:", request.POST)
    print("="*70)
    
    # Get mosaic_id from either POST or GET
    mosaic_id = None
    if request.method == "POST":
        mosaic_id = request.POST.get("mosaic_id")
    else:
        mosaic_id = request.GET.get("mosaic_id")
    
    print(f"Extracted mosaic_id: {mosaic_id}")
    
    if not mosaic_id:
        print("❌ No mosaic_id provided")
        return HttpResponse("Missing mosaic_id parameter", status=400)
    
    try:
        # Fetch the mosaic
        mosaic = Mosaic.objects.prefetch_related("mosaiccubes__cube").get(id=mosaic_id)
        print(f"✅ Found mosaic: {mosaic.name} (ID: {mosaic.id})")
        
        # Generate PDF
        pdf_buffer = generate_teacher_pdf(mosaic)
        print(f"✅ PDF generated successfully")
        print("="*70 + "\n")
        
        # Return PDF response
        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{mosaic.name}_teacher.pdf"'
        return response
        
    except Mosaic.DoesNotExist:
        print(f"❌ Mosaic {mosaic_id} not found")
        return HttpResponse(f"Mosaic with ID {mosaic_id} not found", status=404)
    except Exception as e:
        print(f"❌ ERROR generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*70 + "\n")
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)