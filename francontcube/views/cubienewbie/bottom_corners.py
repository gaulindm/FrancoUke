"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class BottomCornersView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/cubienewbie/bottom-corners.html"
    step_name = "Coins inferieurs"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'bottom-corners-goal',
        'case_1_state': 'bottom-corners-case_1',
        'case_2_state': 'bottom-corners-case_2',
        'case_3_state': 'bottom-corners-case_3',
        'wrong_bottom_corner':'bottom-corners-wrong_bottom_corner',
        'two_wrong_color':'bottom-corners-two_wrong_color',
        'one_wrong_color':'bottom-corners-one_wrong_color',
    }


# Export the view function for URL routing
bottom_corners = BottomCornersView.as_view()