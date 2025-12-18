"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class YellowFaceView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/cubienewbie/yellow-face.html"
    step_name = "Face Jaune"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'yellow-face-goal',
        'before_state': 'yellow-face-before',
        'pattern_no_corner_state': 'yellow-face-case-back',
        'pattern_one_corner_state': 'yellow-face-case-front',
        'pattern_two_corner_state': 'yellow-face-edge-yellow',
    }


# Export the view function for URL routing
yellow_face = YellowFaceView.as_view()