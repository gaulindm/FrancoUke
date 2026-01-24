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


def view_4x4_cube(request):
    """
    View for 4x4x4 cube visualization
    Displays the isometric SVG from my_4x4cube.html
    """
    # Standard 4x4 color palette
    PALETTE_4x4 = {
        'U': '#FFFFFF',  # White
        'R': '#D32F2F',  # Red
        'F': '#2E7D32',  # Green
        'D': '#FFEB3B',  # Yellow
        'L': '#F57C00',  # Orange
        'B': '#1565C0',  # Blue
    }
    
    # Solved state: 96 characters (6 faces × 16 stickers)
    # Order: U(0-15), R(16-31), F(32-47), D(48-63), L(64-79), B(80-95)
    state = request.GET.get('state')
    if state and len(state) == 96:
        cube_state = state
    else:
        # Default solved state
        cube_state = 'U'*16 + 'R'*16 + 'F'*16 + 'D'*16 + 'L'*16 + 'B'*16
    
    # Build facelet to SVG ID mapping (same as in the HTML)
    FACES = [['U', 0], ['R', 16], ['F', 32], ['D', 48], ['L', 64], ['B', 80]]
    facelet_to_id = {}
    for face, start in FACES:
        for i in range(16):
            idx = start + i
            r = i // 4
            c = i % 4
            facelet_to_id[idx] = f'sticker-{face}-{r}-{c}'
    
    # Build SVG color map
    svg_color_map = {}
    for i in range(96):
        facelet = cube_state[i]
        svg_id = facelet_to_id[i]
        svg_color_map[svg_id] = PALETTE_4x4.get(facelet, '#CCCCCC')
    
    context = {
        'svg_color_map_json': json.dumps(svg_color_map),
        'cube_state': cube_state,
        'page_title': '4x4x4 Cube Viewer',
    }
    
    return render(request, 'cube/my_4x4cube.html', context)


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


def f2l_case_detail(request, slug):
    """
    Display detailed view of a single F2L case with Roofpig animation
    """
    cube_state = get_object_or_404(CubeState, slug=slug, method='cfop')
    
    context = {
        'cube_state': cube_state,
        'page_title': cube_state.name,
        'roofpig_config': cube_state.get_roofpig_config(),
    }
    
    return render(request, 'cube/f2l_case_detail.html', context)

def test_top_layer_svg(request):
    """
    Test view for top layer SVG visualization
    Shows different OLL/PLL patterns
    """
    from cube.models import CubeState
    
    # Get some sample cases
    test_cases = []
    
    # Try to get OLL cases
    oll_cases = CubeState.objects.filter(slug__startswith='oll-')[:5]
    test_cases.extend(oll_cases)
    
    # Try to get PLL cases
    pll_cases = CubeState.objects.filter(slug__startswith='pll-')[:5]
    test_cases.extend(pll_cases)
    
    # Create some manual test patterns if no cases exist
    if not test_cases:
        test_cases = [
            {
                'name': 'Test Pattern - Solved',
                'colors': {
                    'U': {
                        '0': {'0': '#FFD700', '1': '#FFD700', '2': '#FFD700'},
                        '1': {'0': '#FFD700', '1': '#FFD700', '2': '#FFD700'},
                        '2': {'0': '#FFD700', '1': '#FFD700', '2': '#FFD700'},
                    },
                    'F': {'0': {'0': '#00D800', '1': '#00D800', '2': '#00D800'}},
                    'R': {'0': {'0': '#C41E3A', '1': '#C41E3A', '2': '#C41E3A'}},
                    'B': {'0': {'0': '#0051BA', '1': '#0051BA', '2': '#0051BA'}},
                    'L': {'0': {'0': '#FF5800', '1': '#FF5800', '2': '#FF5800'}},
                }
            },
            {
                'name': 'Test Pattern - Dot (OLL)',
                'colors': {
                    'U': {
                        '0': {'0': '#808080', '1': '#808080', '2': '#808080'},
                        '1': {'0': '#808080', '1': '#FFD700', '2': '#808080'},
                        '2': {'0': '#808080', '1': '#808080', '2': '#808080'},
                    },
                    'F': {'0': {'0': '#00D800', '1': '#00D800', '2': '#00D800'}},
                    'R': {'0': {'0': '#C41E3A', '1': '#C41E3A', '2': '#C41E3A'}},
                    'B': {'0': {'0': '#0051BA', '1': '#0051BA', '2': '#0051BA'}},
                    'L': {'0': {'0': '#FF5800', '1': '#FF5800', '2': '#FF5800'}},
                }
            },
            {
                'name': 'Test Pattern - Line (OLL)',
                'colors': {
                    'U': {
                        '0': {'0': '#808080', '1': '#808080', '2': '#808080'},
                        '1': {'0': '#FFD700', '1': '#FFD700', '2': '#FFD700'},
                        '2': {'0': '#808080', '1': '#808080', '2': '#808080'},
                    },
                    'F': {'0': {'0': '#00D800', '1': '#00D800', '2': '#00D800'}},
                    'R': {'0': {'0': '#C41E3A', '1': '#C41E3A', '2': '#C41E3A'}},
                    'B': {'0': {'0': '#0051BA', '1': '#0051BA', '2': '#0051BA'}},
                    'L': {'0': {'0': '#FF5800', '1': '#FF5800', '2': '#FF5800'}},
                }
            },
        ]
    
    context = {
        'test_cases': test_cases,
        'page_title': 'Top Layer SVG Test',
    }
    
    return render(request, 'cube/test_top_layer.html', context)