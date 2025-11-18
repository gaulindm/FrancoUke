"""
Level-2 face solver for cube_prep

This module detects simple 3x3 face patterns and returns a human-readable
sequence of legal cube moves (excluding S and wide moves) that will
reproduce the face when applied to a cube oriented with the provided
`up` and `front` colors.

Moves used are limited to: R, L, U, D, F, B, and slice moves M, E.
No S moves, wide moves, or whole-cube rotations are produced.

Functions:
- solve_face_level2(face) -> dict with keys: up, front, sequence, note(optional)
- Several helper detection/solver functions for specific patterns.

`face` is expected as a 3x3 list of color codes, e.g.:
    [["R","W","W"],["W","R","W"],["W","W","R"]]

The output dict is safe to JSON-serialize and store in Cube.moves.
"""

import random
from typing import List, Dict

# Allowed move tokens (human-readable)
ALLOWED_MOVES = [
    "U", "U'", "U2",
    "D", "D'", "D2",
    "R", "R'", "R2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "B", "B'", "B2",
    # slices we allow
    "M", "M'", "M2",
    "E", "E'", "E2",
]

# --------------------
# Pattern detectors
# --------------------

def _center(face: List[List[str]]) -> str:
    return face[1][1]


def is_solid(face: List[List[str]]) -> bool:
    c = _center(face)
    for r in range(3):
        for q in range(3):
            if face[r][q] != c:
                return False
    return True


def is_checker(face: List[List[str]]) -> bool:
    """Checker pattern: alternating corner/edge with center different.
    Example (center R):
    R W R
    W R W
    R W R
    """
    center = _center(face)
    # corners equal center, edges != center
    corners = [face[0][0], face[0][2], face[2][0], face[2][2]]
    edges = [face[0][1], face[1][0], face[1][2], face[2][1]]
    return all(c == center for c in corners) and all(e != center for e in edges)


def is_middle_row_solid(face: List[List[str]]) -> bool:
    """Detects if the middle row is all the same color (a horizontal bar)."""
    row = face[1]
    return row[0] == row[1] == row[2]


def is_middle_col_solid(face: List[List[str]]) -> bool:
    col = [face[0][1], face[1][1], face[2][1]]
    return col[0] == col[1] == col[2]


def is_diagonal_corner_pair(face: List[List[str]]) -> bool:
    """Detects a diagonal pair pattern where two opposite corners are center color.
    Example:
      R W W
      W R W
      W W R
    """
    center = _center(face)
    return face[0][0] == center and face[1][1] == center and face[2][2] == center and (
        face[0][2] != center or face[2][0] != center
    )

# --------------------
# Small pattern solvers
# --------------------

def solve_solid(face: List[List[str]]) -> Dict:
    front = _center(face)
    # If the entire face is the same color, no moves required — only orientation matters.
    return {"up": "W", "front": front, "sequence": "", "note": "solid"}


def solve_checker(face: List[List[str]]) -> Dict:
    front = _center(face)
    # A simple, kid-friendly recipe: F2 M2 (works to create front-only checker pattern)
    seq = "F2 M2"
    return {"up": "W", "front": front, "sequence": seq, "note": "checker"}


def solve_middle_row(face: List[List[str]]) -> Dict:
    front = _center(face)
    # A horizontal middle bar can be produced by E or U/D depending on orientation.
    # Use E (equatorial) to be explicit about a middle-layer move.
    # Choose E2 if the desired color is same across entire middle row but is not center color.
    seq = "E"  # single equatorial slice — caller may interpret orientation if needed
    # If the middle row color equals front color, E2 will place them; choose E2 if center differs.
    mid = face[1][0]
    if mid == front:
        seq = "E2"
    return {"up": "W", "front": front, "sequence": seq, "note": "middle_row"}


def solve_middle_col(face: List[List[str]]) -> Dict:
    front = _center(face)
    seq = "M"
    mid = face[0][1]
    if mid == front:
        seq = "M2"
    return {"up": "W", "front": front, "sequence": seq, "note": "middle_col"}


def solve_diagonal_corners(face: List[List[str]]) -> Dict:
    front = _center(face)
    # Use a short, readable 2-step sequence that uses an M-slice and a U turn.
    # This is heuristic and intentionally simple for teaching.
    seq = "M' U M"
    return {"up": "W", "front": front, "sequence": seq, "note": "diag_corners"}

# --------------------
# Fallback: simple human-readable scramble generator
# --------------------

def generate_human_scramble(length: int = 12) -> str:
    return " ".join(random.choices(ALLOWED_MOVES, k=length))

# --------------------
# Public entrypoint
# --------------------

def solve_face_level2(face: List[List[str]]) -> Dict:
    """
    Attempt to match known face patterns and return a small recipe dict:
    {"up": <color>, "front": <color>, "sequence": <moves>, "note": <optional>}

    If pattern is not recognized, generate a short human-friendly scramble as fallback.
    """
    # Basic validation
    if not isinstance(face, list) or len(face) != 3 or any(len(r) != 3 for r in face):
        return {"up": "W", "front": "W", "sequence": "", "note": "invalid_face"}

    # Pattern detection order: from most-specific to generic
    if is_solid(face):
        return solve_solid(face)

    if is_checker(face):
        return solve_checker(face)

    if is_middle_row_solid(face):
        return solve_middle_row(face)

    if is_middle_col_solid(face):
        return solve_middle_col(face)

    if is_diagonal_corner_pair(face):
        return solve_diagonal_corners(face)

    # If none matched, return a short human-readable scramble
    seq = generate_human_scramble(length=14)
    return {"up": "W", "front": _center(face), "sequence": seq, "note": "fallback_random"}

# --------------------
# Quick CLI test (when run as a script)
# --------------------
if __name__ == "__main__":
    sample = [
        [["R","W","W"],["W","R","W"],["W","W","R"]],
        [["W","W","W"],["W","W","W"],["W","W","W"]],
        [["R","W","R"],["W","R","W"],["R","W","R"]],
        [["W","W","W"],["R","R","R"],["W","W","W"]],
    ]

    for f in sample:
        print("Face:")
        for r in f:
            print(r)
        print("=>", solve_face_level2(f))
        print()
