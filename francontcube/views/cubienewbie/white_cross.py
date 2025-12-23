"""
Step 1: La Croix Blanche (White Cross) - Beginner Method

Form the white cross on the bottom of the cube by aligning white edges
with their matching center colors.
"""

from ..base import StepView, CubeStateLoader


class WhiteCrossView(StepView):
    """
    Step 1: White cross on bottom - Beginner Method.
    
    This is the first solving step where we create a white cross
    on the bottom face with edges aligned to center colors.
    """
    
    template_name = "francontcube/methods/cubienewbie/white-cross.html"
    method_name = "CubieNewbie"  # ← Change from "Apprenti Cubi"
    step_name = "Croix Blanche"
    step_number = 1  # ← NOUVEAU
    step_icon = "plus-circle"
    
    # Navigation
    next_step = "francontcube:beginner_bottom_corners"
    prev_step = None  # First step
    
    # Cube states - use different slugs from Cubie Newbie
    cube_state_slugs = {
        'goal_state': 'white-cross-goal',
        'before_state': 'white-cross-before',
        'after_state': 'white-cross-after',
    }
    
    def get_context_data(self):
            """Override to add progress states as an array."""
            context = super().get_context_data()
            
            # Load progress states (0-4 edges placed)
            progress_slugs = {
                f'progress_{i}': f'white-cross-progress-{i}'
                for i in range(5)
            }
            progress_states, progress_missing = CubeStateLoader.get_multiple(progress_slugs)
            
            # Add progress states as an ordered array
            context['progress_states'] = [
                progress_states[f'progress_{i}'] for i in range(5)
            ]
            
            # Add missing progress slugs to the missing list
            context['missing_slugs'].extend(progress_missing)
            
            return context


# Export the view function for URL routing
white_cross = WhiteCrossView.as_view()