"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class EdgePermutationView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/cubienewbie/edge-permutation.html"
    step_name = "Permutation des aretes"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'edge-perm-goal',
        'goal_needsu_state': 'edge-perm-goal-needsu',
        'no_good_edge_state': 'edge-perm-no-good-edge',
        'one_good_edge_state': 'edge-perm-one-good-edge',
    
    }


# Export the view function for URL routing
edge_permutation = EdgePermutationView.as_view()