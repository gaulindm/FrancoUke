"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class CornerPermutationView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/cubienewbie/corner-permutation.html"
    step_name = "Permutation des coins"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'corner-perm-goal',
        'goal_needsu_state': 'corner-perm-goal-needsu',
        'one_correct_state': 'corner-perm-one-correct',
        'no_correct_state': 'corner-perm-no-correct',
    }


# Export the view function for URL routing
corner_permutation = CornerPermutationView.as_view()