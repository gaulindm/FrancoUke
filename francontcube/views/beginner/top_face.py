"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class TopFaceView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/beginner/top-face.html"
    method_name = "Débutant"
    step_name = "La face du haut"
    step_icon = "flower3"   
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'top-face-goal',
        #'before_state': 'yellow-face-before',
        # 1 sune away
        #'yellow_sune_state': 'yellow-sune',
        # 2 sune away
        'antisune_state': 'antisune',
        'doublesune_state': 'doublesune',
        'pi_state': 'pi',
        #3 sune away
        'superman_state': 'superman',
        'chameleon_state': 'chameleon',
        'bowtie_state': 'bowtie',
        

    }


# Export the view function for URL routing
top_face = TopFaceView.as_view()