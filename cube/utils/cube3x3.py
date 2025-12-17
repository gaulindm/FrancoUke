import json

class Cube3x3:
    """
    Simple backend 3×3 cube representation.
    Faces stored as:
        U, R, F, D, L, B
    Each face is a 3×3 list of colors.
    """

    def __init__(self):
        self.faces = {}
        self._init_solved()

    def _init_solved(self):
        """Initialize a solved cube state."""
        self.faces = {
            "U": [["Y"] * 3 for _ in range(3)],  # Up is Yellow
            "R": [["R"] * 3 for _ in range(3)],  # Right is Red
            "F": [["G"] * 3 for _ in range(3)],  # Front is Green
            "D": [["W"] * 3 for _ in range(3)],  # Down is White
            "L": [["O"] * 3 for _ in range(3)],  # Left is Orange
            "B": [["B"] * 3 for _ in range(3)],  # Back is Blue
        }

    # ----------------------------------------------------------------------
    # Basic stubs for future move logic
    # ----------------------------------------------------------------------
    def move(self, notation):
        """
        Placeholder for future move implementation.
        For now, this does nothing.
        """
        pass

    # ----------------------------------------------------------------------
    # Convert to JSON for the renderer
    # ----------------------------------------------------------------------
    def to_json(self):
        return json.dumps(self.faces)

    # ----------------------------------------------------------------------
    # Beginner Method Step 1 — Daisy
    # ----------------------------------------------------------------------
    def make_daisy(self):
        """Create the beginner-method Daisy on the Up face."""

        # Ensure starting from solved
        self._init_solved()

        # Colors
        W = "W"

        # Place white edges around U-center (yellow)
        self.faces["U"][0][1] = W  # U01
        self.faces["U"][1][0] = W  # U10
        self.faces["U"][1][2] = W  # U12
        self.faces["U"][2][1] = W  # U21

        return self
