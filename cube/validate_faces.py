#!/usr/bin/env python3
"""
validate_faces.py
Checks that your MOVE_MAP permutations preserve cubie structure.
This version is fully path-robust and can be run from ANY directory.
"""

import os
import sys

# ------------------------------------------------------------
# Ensure the project root is on PYTHONPATH
# ------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now the import will always work
from cube.utils.moves import MOVE_MAP


# ------------------------------------------------------------
# Cubie mapping
# ------------------------------------------------------------
# Pieces: 8 corners + 12 edges + 6 centers
# Each cubie is a set of facelet indices
cubie_of = {}

# Corner cubies
corners = [
    (0,  9,  38),   # URF
    (2,  36, 11),   # UFL
    (6,  29, 15),   # ULB
    (8,  17, 27),   # UBR
    (45, 18, 20),   # DRF
    (47, 26, 22),   # DFL
    (51, 24, 33),   # DLB
    (53, 35, 42),   # DBR
]

# Edge cubies
edges = [
    (1, 10),    # UR
    (5, 37),    # UF
    (7, 28),    # UL
    (3, 16),    # UB
    (46, 19),   # DR
    (50, 25),   # DF
    (52, 34),   # DL
    (48, 43),   # DB
    (12, 39),   # FR
    (14, 30),   # FL
    (32, 41),   # LB
    (21, 23),   # BR
]

# Centers (1-stickers, must map to themselves)
centers = [
    (4,),   # U
    (13,),  # R
    (22,),  # F
    (31,),  # D
    (40,),  # L
    (49,),  # B
]

# Build cubie map
for cubie in corners + edges + centers:
    for pos in cubie:
        cubie_of[pos] = cubie


# ------------------------------------------------------------
# Validator
# ------------------------------------------------------------
def validate(name, perm):
    print(f"{name}: ", end="")
    for i in range(54):
        if cubie_of[i] != cubie_of[perm[i]]:
            print("❌ FAIL – cubie mismatch at index", i)
            return
    print("OK ✔ (cubie structure preserved)")


def main():
    print("=== Validating all moves preserve cubie structure ===\n")
    for name, perm in MOVE_MAP.items():
        validate(name, perm)


if __name__ == "__main__":
    main()
