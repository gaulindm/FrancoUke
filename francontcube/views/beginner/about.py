"""
Introduction page: Understanding the 3x3x3 Rubik's Cube

Explains the pieces, structure, and mechanics of the cube before
diving into the solving method.
"""

from ..base import StepView


class AboutView(StepView):
    """
    Introduction to the 3x3x3 Rubik's Cube.
    
    Teaches about:
    - The 6 faces
    - The 3 types of pieces (centers, edges, corners)
    - How the cube mechanism works
    - Basic vocabulary
    """
    
    template_name = "francontcube/methods/beginner/about.html"
    method_name = "Débutant"
    step_number = 1
    step_name = "Le Cube"
    step_icon = "cube"
    
    # Navigation
    next_step = "francontcube:beginner_white_cross"
    prev_step = None

    cube_state_slugs = {
        'solved_state': 'cube-intro-solved',
        'scrambled_state': 'cube-intro-scrambled',
        'faces_state': 'cube-intro-faces',
        'centers_state': 'cube-intro-centers',
        'edges_state': 'cube-intro-edges',
        'corners_state': 'cube-intro-corners',
    }


# Export the view function
about = AboutView.as_view()