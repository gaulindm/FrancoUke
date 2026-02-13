"""
Mosaic overview page.

Displays the list of all steps in the method with their descriptions.
"""

from django.shortcuts import render
from cube.models import CubeState
import json


def mosaic(request):
    """
    Main overview page for Apprenti Cubi method.
    
    Shows all 11 items (3 intro + 7 solving steps + 1 final) with descriptions,
    icons, cube states, and availability status.
    """
    breadcrumbs = [
        {'name': 'Mosaic', 'url': '/francontcube/', 'icon': 'book'},
       # {'name': 'About', 'url': '', 'icon': 'star-fill'},
    ]
    
    # Helper function to get cube state safely
    def get_cube_state(slug):
        try:
            state = CubeState.objects.get(slug=slug)
            # json_state is already a dict (JSONField), just return it as JSON string
            return json.dumps(state.json_state)
        except CubeState.DoesNotExist:
            return None
    
    steps = [
        {
            "name": "1 — A propos",
            "desc": "Au sujet de la méthode présenté pour les nouveaux cubeurs",
            "icon": "bi-cube",
            "url": "/francontcube/mosaic/about/",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "2 — Les mouvements pour preparer votre face",    
            "desc": "Sans vous preocupper du reste du cube",
            "icon": "bi-check-circle",
            "url": "/francontcube/mosaic/mosaic_steps/",
            "available": True,
            "cube_state": None  # No cube for intro        
        },
    ]

    return render(request, "francontcube/mosaic/index.html", {
        "steps": steps,
        "breadcrumbs": breadcrumbs
    })