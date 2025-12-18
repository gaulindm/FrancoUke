"""
Step 1b: La Croix Blanche (White Cross)

Transform the daisy into a white cross on the bottom of the cube.
This step includes progress tracking with 5 intermediate states.
"""

from ..base import StepView, CubeStateLoader


class WhiteCrossView(StepView):
    """
    Step 1b: White cross on bottom.
    
    This is a more complex example that shows how to override get_context_data()
    to add custom logic (in this case, loading progress states as an array).
    """
    
    template_name = "francontcube/methods/cubienewbie/white-cross.html"
    step_name = "Croix Blanche"
    step_icon = "plus-circle"
    
    # Basic cube states
    cube_state_slugs = {
        'goal_state': 'white-cross-goal',
        'before_state': 'white-cross-before',
        'after_state': 'white-cross-after',
        'wrong_state': 'white-cross-wrong',
        'correct_state': 'white-cross-correct',
    }
    
    def get_context_data(self):
        """
        Override to add progress states as an array.
        
        The template expects progress_states as a list of 5 items (0-4 edges placed).
        We load these separately and add them to the context.
        """
        # Get base context (includes basic cube states and breadcrumbs)
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
        
        # Add any missing progress slugs to the missing list
        context['missing_slugs'].extend(progress_missing)
        
        return context


# Export the view function for URL routing
white_cross = WhiteCrossView.as_view()