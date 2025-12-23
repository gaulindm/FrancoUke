"""
Notation page: Learning to read cube move notation

Teaches the standard Singmaster notation used worldwide
for describing cube moves (R, L, U, D, F, B and their variants).
"""

from ..base import StepView


class NotationView(StepView):
    """
    Notation explanation page.
    
    Teaches:
    - The 6 basic moves (R, L, U, D, F, B)
    - Counter-clockwise moves (prime notation: R', U', etc.)
    - Double turns (R2, U2, etc.)
    - How to read complete algorithms
    """
    
    template_name = "francontcube/methods/cubienewbie/notation.html"
    step_name = "La Notation"
    step_icon = "pencil"
    
    cube_state_slugs = {
        # Basic moves (clockwise)
        'r_move_state': 'notation-r-move',
        'l_move_state': 'notation-l-move',
        'u_move_state': 'notation-u-move',
        'd_move_state': 'notation-d-move',
        'f_move_state': 'notation-f-move',
        'b_move_state': 'notation-b-move',
        
        # Counter-clockwise (prime)
        'r_prime_state': 'notation-r-prime',
        'u_prime_state': 'notation-u-prime',
        
        # Double turns
        'r2_state': 'notation-r2',
        'f2_state': 'notation-f2',
    }


# Export the view function
notation = NotationView.as_view()