"""
Introduction page: Understanding the 3x3x3 Rubik's Cube

Explains the pieces, structure, and mechanics of the cube before
diving into the solving method.
"""

from ..base import StepView


class CubeIntroView(StepView):
    """
    Introduction to the 3x3x3 Rubik's Cube.
    
    Teaches about:
    - The 6 faces
    - The 3 types of pieces (centers, edges, corners)
    - How the cube mechanism works
    - Basic vocabulary
    """
    
    template_name = "francontcube/methods/cubienewbie/cube-intro.html"
    step_name = "Le Cube"
    step_icon = "cube"
    
    cube_state_slugs = {
        'solved_state': 'cube-intro-solved',
        'scrambled_state': 'cube-intro-scrambled',
        'faces_state': 'cube-intro-faces',
        'centers_state': 'cube-intro-centers',
        'edges_state': 'cube-intro-edges',
        'corners_state': 'cube-intro-corners',
    }


# Export the view function
cube_intro = CubeIntroView.as_view()