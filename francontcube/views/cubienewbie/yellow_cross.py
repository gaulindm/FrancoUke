"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class YellowCrossView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/cubienewbie/yellow-cross.html"
    step_name = "Croix jaune"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'yellow-cross-goal',
        #'before_state': 'yellow-cross-before',
        'pattern_dot_state': 'yellow-cross-pattern-dot',
        'pattern_l_state': 'yellow-cross-pattern-l',
        'pattern_line_state': 'yellow-cross-pattern-line',
    }


# Export the view function for URL routing
yellow_cross = YellowCrossView.as_view()