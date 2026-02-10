# views.py

import os
import random
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


from .models import Cube, Mosaic



#from .settings import MOVE_ICONS_DIR, CUBE_COLOR_MAP







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

from .models import Cube, Mosaic, MosaicCube

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import Mosaic, Cube, MosaicCube


@csrf_exempt
def save_mosaic(request):
    """
    Save a new mosaic.
    Supports both square and rectangular grids.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    try:
        # Get POST data
        mosaic_json = request.POST.get('mosaic_json')
        mosaic_name = request.POST.get('mosaic_name', 'Untitled Mosaic')
        cubes_per_side = int(request.POST.get('cubes_per_side', 3))
        
        if not mosaic_json:
            return JsonResponse({
                'success': False, 
                'error': 'No mosaic data provided'
            }, status=400)
        
        # Parse JSON
        try:
            cubes_data = json.loads(mosaic_json)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False, 
                'error': f'Invalid JSON: {str(e)}'
            }, status=400)
        
        # Validate cubes_data
        if not isinstance(cubes_data, list):
            return JsonResponse({
                'success': False,
                'error': 'mosaic_json must be an array'
            }, status=400)
        
        # 🔴 NOUVEAU: Détecte automatiquement les dimensions
        total_cubes = len(cubes_data)
        cols = cubes_per_side
        rows = total_cubes // cols
        
        # Valide que c'est bien rectangulaire
        if rows * cols != total_cubes:
            return JsonResponse({
                'success': False,
                'error': f'Invalid grid: {total_cubes} cubes cannot form a {rows}×{cols} grid'
            }, status=400)
        
        # Create mosaic
        mosaic = Mosaic.objects.create(
            name=mosaic_name
        )
        
        # Link to leader if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'leader_profile'):
                mosaic.created_by_leader = request.user.leader_profile
                mosaic.save()
        
        # Create cubes
        for idx, cube_colors in enumerate(cubes_data):
            row = idx // cols
            col = idx % cols
            
            # Validate cube_colors format
            if not isinstance(cube_colors, list) or len(cube_colors) != 3:
                print(f"Warning: Invalid cube at index {idx}, skipping")
                continue
            
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
        
        return JsonResponse({
            'success': True,
            'mosaic_id': mosaic.id
        })
        
    except Exception as e:
        # Log error for debugging
        import traceback
        print("=" * 60)
        print("ERROR in save_mosaic:")
        print(f"Error: {e}")
        traceback.print_exc()
        print("=" * 60)
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def mosaic_list(request):
    mosaics = Mosaic.objects.all().order_by("-created_at")

    return JsonResponse([
        {
            "id": m.id,
            "name": m.name,
        }
        for m in mosaics
    ], safe=False)


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


from django.http import JsonResponse
from .models import Mosaic

def mosaic_detail(request, mosaic_id):
    mosaic = Mosaic.objects.get(id=mosaic_id)

    cubes = []
    max_col = mosaic.cube_cols

    for mc in mosaic.mosaiccubes.all().order_by("row", "col"):
        cubes.append(mc.cube.colors)

    return JsonResponse({
        "id": mosaic.id,
        "name": mosaic.name,
        "cubes_per_side": mosaic.cube_cols,
        "cubes": cubes,
    })

