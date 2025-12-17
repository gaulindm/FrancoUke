# cube/utils/cube.py

from .moves import MOVE_MAP

class Cube:
    """
    54-character facelet representation:
    Order = U R F D L B  (each face has 9 stickers)
    """

    SOLVED = (
        "U"*9 +
        "R"*9 +
        "F"*9 +
        "D"*9 +
        "L"*9 +
        "B"*9
    )

    def __init__(self, state=None):
        self.state = state or Cube.SOLVED

    def __str__(self):
        return self.state

    def copy(self):
        return Cube(self.state[:])

    def apply_move(self, move):
        """Applies a single move: 'R', 'U'', 'F2', etc."""
        if move not in MOVE_MAP:
            raise ValueError(f"Invalid move: {move}")

        perm = MOVE_MAP[move]
        self.state = ''.join(self.state[i] for i in perm)

    def apply_alg(self, alg):
        """Applies an algorithm string like: 'R U R' U'' """
        moves = alg.split()
        for m in moves:
            self.apply_move(m)

    def test_move(self, move):
        print(f"\n=== Testing {move} followed by inverse ===")
        start = self.state
        print("Start :", repr(start))

        self.apply_move(move)
        after = self.state
        print("After :", repr(after))

        # apply inverse
        inv = move[:-1] if move.endswith("'") else move + "'" if move in ["R","U","F","L","D","B"] else move
        self.apply_move(inv)
        final = self.state
        print("Final :", repr(final))

        if final == start:
            print("PASS")
        else:
            print("FAIL")


