"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class TopCrossView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/beginner/top-cross.html"
    method_name = "Débutant"
    step_name = "Croix du haut"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'top-cross-goal',
        #'before_state': 'yellow-cross-before',
        'pattern_dot_state': 'top-cross-pattern-dot',
        'pattern_l_state': 'top-cross-pattern-l',
        'pattern_line_state': 'top-cross-pattern-line',
    }


# Export the view function for URL routing
top_cross = TopCrossView.as_view()