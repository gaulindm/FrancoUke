# views.py - VERSION CORRIGÉE

import os
import random
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Cube, Mosaic, MosaicCube


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