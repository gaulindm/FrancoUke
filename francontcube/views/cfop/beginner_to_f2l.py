"""
Bridge page: From Beginner Method to F2L.

Shows students how the second layer algorithm they already know
is actually F2L in disguise!
"""

from django.urls import reverse
from ..base import StepView


class BeginnerToF2LView(StepView):
    """
    Educational bridge page showing how beginner second layer = F2L.
    
    This page helps students realize they already know F2L concepts:
    - U' F' U F (4 moves) = Pairing the corner and edge
    - U R U' R' (4 moves) = Inserting the pair
    """
    
    template_name = "francontcube/methods/cfop/beginner_to_f2l.html"
    method_name = "CFOP"
    step_name = "De Débutant à F2L"
    step_icon = "lightbulb-fill"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'case_left_state': 'beg-second-layer-case-left',
        'case_f2l_01_state':'f2l-01',
        # You can add more cube states as you create them:
        # 'case_left_state': 'beg-second-layer-case-left',
        # 'pairing_demo_state': 'f2l-pairing-demo',
        # 'insertion_demo_state': 'f2l-insertion-demo',
    }
    
    
# Export the view function for URL routing
beginner_to_f2l_bridge = BeginnerToF2LView.as_view()