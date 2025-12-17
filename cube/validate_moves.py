# validate_moves.py
from utils import moves  # imports your moves module
from pprint import pprint

MOVE_MAP = moves.MOVE_MAP

def inverse(p):
    inv = [0]*54
    for i, v in enumerate(p):
        inv[v] = i
    return inv

def compose(p, q):
    return [q[p[i]] for i in range(54)]

def is_identity(p):
    return all(p[i] == i for i in range(54))

def show_failures(name, p):
    inv = inverse(p)
    comp = compose(p, inv)   # should be identity
    if is_identity(comp):
        print(f"{name}: OK (perm ∘ inv = id)")
        return True
    print(f"{name}: FAIL (perm ∘ inv != id)")
    bad = [i for i in range(54) if comp[i] != i]
    print(f" {len(bad)} mismatching positions: {bad}")
    print(" For each mismatching index i: comp[i] => expected i")
    for i in bad:
        print(f"  index {i}: comp[{i}] = {comp[i]}  (should be {i})")
    # also show the mapping perm[i] for bad indices
    print("\n perm mappings for bad indices (destination <- source):")
    for i in bad:
        print(f"  dest {i} <- src {p[i]}")
    print("\nInverse mappings for those same indices (inv):")
    for i in bad:
        print(f"  inv[{i}] = {inv[i]}")
    return False

def main():
    failing = []
    for name in sorted(MOVE_MAP.keys()):
        p = MOVE_MAP[name]
        ok = show_failures(name, p)
        if not ok:
            failing.append(name)
        print("-"*60)
    if failing:
        print("Moves that failed inverse test:", failing)
    else:
        print("All moves passed perm ∘ inv = identity check.")

if __name__ == "__main__":
    main()
