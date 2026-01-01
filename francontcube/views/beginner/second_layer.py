"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class SecondLayerView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/beginner/second-layer.html"
    method_name = "Débutant"

    step_name = "Couche du milieu"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'second-layer-goal',
        'before_state': 'second-layer-before',
        'case_back_state': 'second-layer-case-back',
        'case_front_state': 'second-layer-case-front',
        'edge_yellow_state': 'second-layer-edge-yellow',
        'edge_stuck_state': 'second-layer-edge-stuck',

    }


# Export the view function for URL routing
second_layer = SecondLayerView.as_view()