"""
Step 1: Cross - CFOP Method
"""

from ..base import StepView


class CrossView(StepView):
    """
    Step 1: White cross on bottom - CFOP Method.
    
    In CFOP, the cross should be solved efficiently (under 8 moves ideally)
    while planning ahead for F2L pairs.
    """
    
    template_name = "francontcube/methods/cfop/cross.html"
    method_name = "CFOP"
    step_name = "Cross"
    step_number = 1
    step_icon = "plus-circle"
    
    # Navigation
    next_step = "francontcube:cfop_f2l"
    prev_step = None
    
    # Cube states
    cube_state_slugs = {
        'goal_state': 'cfop-cross-goal',
        'example_1': 'cfop-cross-example-1',
    }


# Export
cross = CrossView.as_view()