"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class YellowFaceView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "francontcube/methods/cubienewbie/yellow-face.html"
    step_name = "Face Jaune"
    step_icon = "flower3"   
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'yellow-face-goal',
        'before_state': 'yellow-face-before',
        # 1 sune away
        'yellow_sune_state': 'yellow-sune',
        # 2 sune away
        'yellow_antisune_state': 'yellow-antisune',
        'yellow_doublesune_state': 'yellow-doublesune',
        'yellow_pi_state': 'yellow-pi',
        #3 sune away
        'yellow_superman_state': 'yellow-superman',
        'yellow_chameleon_state': 'yellow-chameleon',
        'yellow_bowtie_state': 'yellow-bowtie',
        

    }


# Export the view function for URL routing
yellow_face = YellowFaceView.as_view()