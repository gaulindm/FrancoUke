from django.shortcuts import render
from cube.models import CubeState
import json

def mosaic_steps(request):

    cube_state_slugs = {
        'case_1_state': 'bottom-corners-case_1',
        'case_2_state': 'bottom-corners-case_2',
        'case_3_state': 'bottom-corners-case_3',
    }

    context = {}
    missing_slugs = []

    for context_key, slug in cube_state_slugs.items():
        try:
            cube_state = CubeState.objects.get(slug=slug)
            context[context_key] = json.dumps(cube_state.json_state)
        except CubeState.DoesNotExist:
            context[context_key] = None
            missing_slugs.append(slug)

    context["missing_slugs"] = missing_slugs

    return render(request, "francontcube/mosaic/mosaic_steps.html", context)
