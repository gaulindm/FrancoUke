# cube/views.py

import json
from .utils.cube import Cube            # your Cube class
from .utils.svg_map import FACELET_TO_SVG_ID, COLOR_HEX
from django.shortcuts import render, get_object_or_404

from .utils.cube3x3 import Cube3x3
from cube.models import CubeState


def view_cube(request):
    # For demo: either create a cube or accept a state via query param
    # Example: ?state=UUU... (54 chars)
    state = request.GET.get('state')
    if state and len(state) == 54:
        cube = Cube(state=state)
    else:
        cube = Cube()  # solved by default

    # Build mapping: svg_id -> color hex
    svg_color_map = {}
    for index, svg_id in FACELET_TO_SVG_ID.items():
        facelet = cube.state[index]  # letter like 'U' 'R' etc
        svg_color_map[svg_id] = COLOR_HEX.get(facelet, "#CCCCCC")

    # Pass as JSON safe string so template JS can use it
    return render(request, "cube/my_3x3cube.html", {
        "svg_color_map_json": json.dumps(svg_color_map)
    })

def index(request):
    return render(request, "cube/index.html")

def all_icons(request):
    return render(request, "cube/all-icons.html")

def algorithm_viewer(request):
    return render(request, "cube/algorithm-viewer.html")

def browser(request):
    """
    Interactive icon browser for algorithms
    """
    algorithms = {
        "Sexy Move (R U R' U')": ["R", "U", "Rprime", "Uprime"],
        "Sledgehammer (R' F R F')": ["Rprime", "F", "R", "Fprime"],
        "Corner Insert (R' D' R D)": ["Rprime", "Dprime", "R", "D"],
        "Edge Insert (R U R' U' F' U' F)": [
            "R", "U", "Rprime", "Uprime", "Fprime", "Uprime", "F"
        ],
    }

    return render(request, "cube/browser.html", {
        "algorithms": algorithms
    })


def demo_backend_cube(request):
    cube = Cube3x3()
    context = {
        "cube_json": cube.to_json(),
    }
    return render(request, "cube/demo_backend_cube.html", context)


def demo_backend_svg(request):
    cube = Cube3x3()
    context = {
        "cube_json": cube.to_json(),
    }
    return render(request, "cube/demo_backend_svg.html", context)



def demo_daisy(request):
    daisy = get_object_or_404(CubeState, slug="scrambled-white-edges")
    return render(request, "cube/demo_daisy.html", {
        "json_state": daisy.json_state
    })
