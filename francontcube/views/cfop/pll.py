"""
Step 4: PLL (Permutation of Last Layer) - CFOP Method
"""

from ..base import StepView


class PLLView(StepView):
    """
    Step 4: Permutation of Last Layer - CFOP Method.
    
    Permute the pieces of the last layer to solve the cube.
    There are 21 PLL cases to learn for full CFOP.
    """
    
    template_name = "francontcube/methods/cfop/pll.html"
    method_name = "CFOP"
    step_name = "PLL"
    step_number = 4
    step_icon = "shuffle"
    
    # Navigation
    next_step = None  # Last step
    prev_step = "francontcube:cfop_oll"
    
    # Cube states - we'll add PLL cases later
    cube_state_slugs = {
        'goal_state': 'cfop-pll-goal',
    }


# Export
pll = PLLView.as_view()