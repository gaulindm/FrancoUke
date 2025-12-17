# cube/utils/moves.py
# Programmatic generation of all 18 WCA facelet permutations (6x9 block format).
# STANDARD SINGMASTER LAYOUT:
# U = 0..8, R = 9..17, F = 18..26, D = 27..35, L = 36..44, B = 45..53

def perm(*rows):
    """Concatenate six 9-element rows into a 54-element permutation list."""
    return [x for row in rows for x in row]

def inverse(p):
    inv = [0]*54
    for i, v in enumerate(p):
        inv[v] = i
    return inv

def square(p):
    return [p[p[i]] for i in range(54)]

# faces (row-major)
U = list(range(0,9))
R = list(range(9,18))
F = list(range(18,27))
D = list(range(27,36))
L = list(range(36,45))
B = list(range(45,54))

def top(face):    return [face[0], face[1], face[2]]
def right(face):  return [face[2], face[5], face[8]]
def bottom(face): return [face[6], face[7], face[8]]
def left(face):   return [face[0], face[3], face[6]]

# clockwise face rotation map (new_pos[i] takes old_pos[CW_FACE_MAP[i]])
CW_FACE_MAP = [6,3,0, 7,4,1, 8,5,2]

def make_move(face_inds, cw_map, side_strips):
    """
    Build a 54-entry permutation where new_state[i] = old_state[perm[i]].

    face_inds: list of 9 indices (the face)
    cw_map: list of 9 indices mapping target->source within the face (for CW)
    side_strips: list of four (indices_list_of_length_3, reversed_bool) tuples
                 listed in cycle order (source -> next destination)
    """
    perm_list = list(range(54))

    # rotate the face itself (CW)
    for tgt_idx in range(9):
        tgt = face_inds[tgt_idx]
        src = face_inds[cw_map[tgt_idx]]
        perm_list[tgt] = src

    # cycle side strips (source -> next)
    for i in range(4):
        source_strip, source_rev = side_strips[i]
        dest_strip, dest_rev = side_strips[(i+1) % 4]

        source_ordered = list(reversed(source_strip)) if source_rev else list(source_strip)
        dest_ordered = list(reversed(dest_strip)) if dest_rev else list(dest_strip)

        for j in range(3):
            perm_list[dest_ordered[j]] = source_ordered[j]

    return perm_list

# Build canonical moves for Singmaster indexing.
# The reversal flags ensure sticker orientation matches when moving between faces.

U_move = make_move(U, CW_FACE_MAP,
                   [(top(F), False), (top(R), False), (top(B), False), (top(L), False)])

R_move = make_move(R, CW_FACE_MAP,
                   [(right(U), False), (right(F), False), (right(D), False), (left(B), True)])

F_move = make_move(F, CW_FACE_MAP,
                   [(bottom(U), False), (left(R), False), (top(D), True), (right(L), True)])

D_move = make_move(D, CW_FACE_MAP,
                   [(bottom(F), False), (bottom(R), False), (bottom(B), False), (bottom(L), False)])

L_move = make_move(L, CW_FACE_MAP,
                   [(left(U), False), (right(B), True), (left(D), False), (left(F), False)])

B_move = make_move(B, CW_FACE_MAP,
                   [(top(U), False), (left(L), True), (bottom(D), True), (right(R), True)])

# Convenience: primes and doubles
U_PRIME = inverse(U_move);  U2 = square(U_move)
R_PRIME = inverse(R_move);  R2 = square(R_move)
F_PRIME = inverse(F_move);  F2 = square(F_move)
D_PRIME = inverse(D_move);  D2 = square(D_move)
L_PRIME = inverse(L_move);  L2 = square(L_move)
B_PRIME = inverse(B_move);  B2 = square(B_move)

# Create block-format 6x9 perm constants (human-readable)
def to_block(p):
    """Return a list of 6 lists (each 9 ints)."""
    return [p[0:9], p[9:18], p[18:27], p[27:36], p[36:45], p[45:54]]

U_block = to_block(U_move)
R_block = to_block(R_move)
F_block = to_block(F_move)
D_block = to_block(D_move)
L_block = to_block(L_move)
B_block = to_block(B_move)

# Expose the 6×9 perm(...) style constants (your preferred format)
U = perm(*U_block)
R = perm(*R_block)
F = perm(*F_block)
D = perm(*D_block)
L = perm(*L_block)
B = perm(*B_block)

U_PRIME = inverse(U)
U2 = square(U)
R_PRIME = inverse(R)
R2 = square(R)
F_PRIME = inverse(F)
F2 = square(F)
D_PRIME = inverse(D)
D2 = square(D)
L_PRIME = inverse(L)
L2 = square(L)
B_PRIME = inverse(B)
B2 = square(B)

# Final MOVE_MAP used by Cube.apply_move (54-element perms)
MOVE_MAP = {
    "U": U, "U'": U_PRIME, "U2": U2,
    "R": R, "R'": R_PRIME, "R2": R2,
    "F": F, "F'": F_PRIME, "F2": F2,
    "D": D, "D'": D_PRIME, "D2": D2,
    "L": L, "L'": L_PRIME, "L2": L2,
    "B": B, "B'": B_PRIME, "B2": B2
}

# Helpful: also export block-style versions as facts if you want to inspect in REPL
BLOCKS = {
    "U": U_block, "R": R_block, "F": F_block,
    "D": D_block, "L": L_block, "B": B_block
}
