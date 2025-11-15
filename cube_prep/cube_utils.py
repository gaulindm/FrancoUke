# cube_utils.py
from cube_prep.models import Cube
import random

MOVES = ["U", "U'", "U2",
         "R", "R'", "R2",
         "F", "F'", "F2",
         "L", "L'", "L2",
         "D", "D'", "D2",
         "B", "B'", "B2"]

def generate_moves_for_face(target_face):
    """
    target_face = list of 9 colors: ["W","R","B","B","W","G", ...]
    """

    attempt_limit = 500  # prevents infinite loops

    for _ in range(attempt_limit):
        cube = Cube()
        moves = []

        # random scramble
        for _ in range(15):
            mv = random.choice(MOVES)
            cube.apply_move(mv)
            moves.append(mv)

        # check front face
        if cube.get_face("F") == target_face:
            return " ".join(moves)

    return ""  # give up — admin panel will show blank



def generate_synthetic_moves(face_colors):
    """
    This does NOT solve the cube.

    It generates a random scramble of 10–20 moves.
    This scramble is what the admin panel will store as “moves”.
    Later, when we implement the real algorithm, you plug it in here.
    """

    length = random.randint(10, 20)
    moves = [random.choice(MOVES) for _ in range(length)]
    return " ".join(moves)




def generate_face_moves(target_face):
    """
    Given a 3x3 target_face array of colors, generate moves to 
    recreate it from a solved face (all 'W').
    Returns a human-readable move sequence string.
    """
    # start with solved white face
    face = [["W"]*3 for _ in range(3)]
    moves = []

    # Naive algorithm: iterate over positions and match colors
    for i in range(3):
        for j in range(3):
            if face[i][j] != target_face[i][j]:
                # rotate row
                for _ in range(3):
                    face[i] = face[i][-1:] + face[i][:-1]
                    moves.append(f"row{i}_right")
                    if face[i][j] == target_face[i][j]:
                        break
                # rotate column
                for _ in range(3):
                    col = [face[r][j] for r in range(3)]
                    col = col[-1:] + col[:-1]
                    for r in range(3):
                        face[r][j] = col[r]
                    moves.append(f"col{j}_down")
                    if face[i][j] == target_face[i][j]:
                        break

    # return move sequence as string
    return " ".join(moves)
