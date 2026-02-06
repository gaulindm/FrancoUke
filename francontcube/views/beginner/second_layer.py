"""
Step 3: Second Layer (Middle Layer Edges)

Place the 4 middle layer edges to complete the first two layers.
This is part of the Cubie Newbie method.
"""

from ..base import StepView


class SecondLayerView(StepView):
    """
    Step 3: Place the second layer edges.
    
    This step teaches how to insert the 4 middle layer edges
    using two mirror algorithms.
    """
    
    template_name = "francontcube/methods/beginner/second-layer.html"
    method_name = "Débutant"

    step_name = "Couche du milieu"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'beg-second-layer-goal',
        'case_left_state': 'beg-second-layer-case-left',
        'case_right_state': 'beg-second-layer-case-right',
        'edge_yellow_state': 'beg-second-layer-edge-yellow',
        'edge_stuck_state': 'beg-second-layer-edge-stuck',
    }


# Export the view function for URL routing
second_layer = SecondLayerView.as_view()