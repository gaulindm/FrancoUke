# legality_test.py
# Validates all Rubik's Cube 3×3 facelet permutations in MOVE_MAP

from cube.utils.moves import MOVE_MAP

# Define facelet groups
CORNERS = [
    [0,  2,  8],   # ULB, URB, URF, ULF
    [6,  8,  2],
    [18, 20, 26],
    [24, 26, 20],
    [36, 38, 44],
    [42, 44, 38],
    [45, 47, 53],
    [51, 53, 47]
]

EDGES = [
    [1,  5], [3,  7], [ 9, 11], [12, 14],
    [19, 23], [21, 25], [28, 32], [30, 34],
    [37, 41], [39, 43], [46, 50], [48, 52]
]

CENTERS = [4, 13, 22, 31, 40, 49]

def is_permutation(p):
    return sorted(p) == list(range(54))

def parity(p):
    p = p[:]  # copy
    visited = [False] * 54
    total = 0
    for i in range(54):
        if not visited[i]:
            length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = p[j]
                length += 1
            if length > 1:
                total ^= (length & 1)
    return total

def check_cubie_type(p):
    # Corners:
    for corner in CORNERS:
        new = [p[i] for i in corner]
        if not any(set(new) == set(c) for c in CORNERS):
            return False

    # Edges:
    for edge in EDGES:
        new = [p[i] for i in edge]
        if not any(set(new) == set(e) for e in EDGES):
            return False

    # Centers must stay centers:
    for c in CENTERS:
        if p[c] not in CENTERS:
            return False

    return True


def check_move(name, perm):
    errors = []

    # 1. Valid permutation of 0–53
    if not is_permutation(perm):
        errors.append("Not a valid permutation")

    # 2. Even parity
    if parity(perm) != 0:
        errors.append("Odd permutation (illegal move)")

    # 3. Cubie type preserved
    if not check_cubie_type(perm):
        errors.append("Cubie type violation")

    return errors


if __name__ == "__main__":
    print("=== Rubik's Cube Move Legality Test ===")
    bad = False

    for name, perm in MOVE_MAP.items():
        errs = check_move(name, perm)
        if errs:
            bad = True
            print(f"[FAIL] {name}:")
            for e in errs:
                print("   -", e)
        else:
            print(f"[OK]   {name}")

    if not bad:
        print("\nAll move tables are valid! 🎉")
    else:
        print("\nSome moves failed legality tests. ❌")
