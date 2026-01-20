"""
Step 3: OLL (Orientation of Last Layer) - CFOP Method
"""

from ..base import StepView


class OLLView(StepView):
    """
    Step 3: Orientation of Last Layer - CFOP Method.
    
    Orient all pieces of the last layer to make the top face all yellow.
    There are 57 OLL cases to learn for full CFOP.
    """
    
    template_name = "francontcube/methods/cfop/oll.html"
    method_name = "CFOP"
    step_name = "OLL"
    step_number = 3
    step_icon = "brightness-high"
    
    # Navigation
    next_step = "francontcube:cfop_pll"
    prev_step = "francontcube:cfop_f2l"
    
    # Cube states - we'll add OLL cases later
    cube_state_slugs = {
        'goal_state': 'cfop-oll-goal',
    }


# Export
oll = OLLView.as_view()