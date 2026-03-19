# populate_oll.py
# Peuple les 57 cas OLL dans CubeState
# Lancer avec: python manage.py shell < populate_oll.py

from cube.models import CubeState

# ──────────────────────────────────────────────────────────────────────────────
# Format: (step_number, algorithm, category, difficulty, description)
#
# Catégories (matching oll_pll.py):
#   oll-cross    → 1  cas  (skip)
#   oll-dot      → 8  cas  (aucune arête orientée)
#   oll-line     → 8  cas  (deux arêtes opposées)
#   oll-l-shape  → 6  cas  (deux arêtes adjacentes)
#   oll-square   → 4  cas  (bloc 2×2 dans le coin)
#   oll-lightning→ 8  cas  (forme d'éclair)
#   oll-fish     → 4  cas  (forme poisson / Sune)
#   oll-knight   → 8  cas  (déplacement cavalier)
#   oll-awkward  → 4  cas  (cas inhabituels)
#   oll-t-shape  → 2  cas  (forme T)
#   oll-c-shape  → 2  cas  (forme C)
#   oll-w-shape  → 2  cas  (forme W)
#                  57 total
# ──────────────────────────────────────────────────────────────────────────────

OLL_DATA = [

    # ═══════════════════════════════════════════════════════════
    # CROSS / SKIP (1)
    # ═══════════════════════════════════════════════════════════
    (57, '',
     'oll-cross', 'facile',
     'OLL Skip — la dernière couche est déjà orientée, aucun algorithme nécessaire'),

    # ═══════════════════════════════════════════════════════════
    # DOT (8) — aucune arête orientée sur le dessus
    # ═══════════════════════════════════════════════════════════
    (1,  "R U2 R2 F R F' U2 R' F R F'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée, coins en diagonale"),

    (2,  "F R U R' U' F' f R U R' U' f'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée, deux paires de coins"),

    (3,  "f R U R' U' f' U' F R U R' U' F'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée, coins adjacents"),

    (4,  "f R U R' U' f' U F R U R' U' F'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée, coins adjacents miroir"),

    (17, "R U R' U R' F R F' R U2 R'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée"),

    (18, "r U R' U R U2 r2 U' R U' R' U2 r",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée"),

    (19, "M U R U R' U' M' R' F R F'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée"),

    (20, "M U R U R' U' M2 U R U' r'",
     'oll-dot', 'difficile',
     "Dot — aucune arête orientée"),

    # ═══════════════════════════════════════════════════════════
    # LINE (8) — deux arêtes opposées orientées
    # ═══════════════════════════════════════════════════════════
    (15, "r' U' r R' U' R U r' U r",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées"),

    (16, "r U r' R U R' U' r U' r'",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées, miroir"),

    (28, "r U R' U' M R U R' U'",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées"),

    (47, "F' L' U' L U L' U' L U F",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées"),

    (48, "F R U R' U' R U R' U' F'",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées"),

    (49, "r U' r2 U r2 U r2 U' r",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées"),

    (50, "r' U r2 U' r2 U' r2 U r'",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées, miroir"),

    (51, "f R U R' U' R U R' U' f'",
     'oll-line', 'moyen',
     "Ligne — deux arêtes opposées orientées"),

    # ═══════════════════════════════════════════════════════════
    # L-SHAPE (6) — deux arêtes adjacentes orientées
    # ═══════════════════════════════════════════════════════════
    (5,  "r' U2 R U R' U r",
     'oll-l-shape', 'moyen',
     "Forme L — deux arêtes adjacentes orientées"),

    (6,  "r U2 R' U' R U' r'",
     'oll-l-shape', 'moyen',
     "Forme L — deux arêtes adjacentes orientées, miroir"),

    (9,  "R U R' U' R' F R2 U R' U' F'",
     'oll-l-shape', 'moyen',
     "Forme L — deux arêtes adjacentes orientées"),

    (10, "R U R' U R' F R F' R U2 R'",
     'oll-l-shape', 'moyen',
     "Forme L — deux arêtes adjacentes orientées"),

    (44, "f R U R' U' f'",
     'oll-l-shape', 'facile',
     "Forme L — algorithme court, deux arêtes adjacentes"),

    (45, "F R U R' U' F'",
     'oll-l-shape', 'facile',
     "Forme L — algorithme court, miroir de OLL 44"),

    # ═══════════════════════════════════════════════════════════
    # SQUARE (4) — bloc 2×2 dans le coin
    # ═══════════════════════════════════════════════════════════
    (7,  "r U R' U' r' R U R U' R'",
     'oll-square', 'moyen',
     "Carré — bloc 2×2 de stickers blancs dans le coin"),

    (8,  "r' U' R U r R' U' R' U R",
     'oll-square', 'moyen',
     "Carré — bloc 2×2 de stickers blancs dans le coin, miroir"),

    (11, "r' R2 U R' U R U2 R' U M'",
     'oll-square', 'difficile',
     "Carré — bloc 2×2 dans le coin avec slice move"),

    (12, "M' R' U' R U' R' U2 R U' M",
     'oll-square', 'difficile',
     "Carré — bloc 2×2 dans le coin avec slice move, miroir"),

    # ═══════════════════════════════════════════════════════════
    # LIGHTNING (8) — forme d'éclair
    # ═══════════════════════════════════════════════════════════
    (13, "F U R U' R2 F' R U R U' R'",
     'oll-lightning', 'moyen',
     "Éclair — forme d'éclair sur le côté droit"),

    (14, "R' F R U R' F' R F U' F'",
     'oll-lightning', 'moyen',
     "Éclair — forme d'éclair sur le côté gauche"),

    (30, "F R' F R2 U' R' U' R U R' F2",
     'oll-lightning', 'difficile',
     "Éclair — forme d'éclair complexe"),

    (31, "R' U' F U R U' R' F' R",
     'oll-lightning', 'moyen',
     "Éclair — forme d'éclair"),

    (32, "R U B' U' R' U R B R'",
     'oll-lightning', 'moyen',
     "Éclair — forme d'éclair avec B move"),

    (53, "r' U2 R U R' U' R U R' U r",
     'oll-lightning', 'difficile',
     "Éclair — forme d'éclair avec wide move"),

    (54, "r U2 R' U' R U R' U' R U' r'",
     'oll-lightning', 'difficile',
     "Éclair — forme d'éclair avec wide move, miroir"),

    (55, "R' F R U R U' R2 F' R2 U' R' U R U R'",
     'oll-lightning', 'difficile',
     "Éclair — algorithme long, cas difficile"),

    # ═══════════════════════════════════════════════════════════
    # FISH (4) — forme poisson / Sune
    # ═══════════════════════════════════════════════════════════
    (26, "R U2 R' U' R U' R'",
     'oll-fish', 'facile',
     "Poisson — Anti-Sune, phares à gauche"),

    (27, "R U R' U R U2 R'",
     'oll-fish', 'facile',
     "Poisson — Sune, phares à droite"),

    (35, "R U2 R2 F R F' R U2 R'",
     'oll-fish', 'moyen',
     "Poisson — variante Sune sans arêtes orientées"),

    (37, "F R' F' R U R U' R'",
     'oll-fish', 'moyen',
     "Poisson — variante Anti-Sune"),

    # ═══════════════════════════════════════════════════════════
    # KNIGHT (8) — déplacement en L comme le cavalier
    # ═══════════════════════════════════════════════════════════
    (24, "r U R' U' r' F R F'",
     'oll-knight', 'moyen',
     "Cavalier — déplacement en L, côté droit"),

    (25, "F' r U R' U' r' F R",
     'oll-knight', 'moyen',
     "Cavalier — déplacement en L, côté gauche"),

    (29, "R U R' U' R U' R' F' U' F R U R'",
     'oll-knight', 'difficile',
     "Cavalier — déplacement en L complexe"),

    (39, "L F' L' U' L U F U' L'",
     'oll-knight', 'moyen',
     "Cavalier — déplacement en L, main gauche"),

    (40, "R' F R U R' U' F' U R",
     'oll-knight', 'moyen',
     "Cavalier — déplacement en L"),

    (41, "R U R' U R U2 R' F R U R' U' F'",
     'oll-knight', 'difficile',
     "Cavalier — déplacement en L, long"),

    (42, "R' U' R U' R' U2 R F R U R' U' F'",
     'oll-knight', 'difficile',
     "Cavalier — déplacement en L, long miroir"),

    (52, "R U R' U R U' B U' B' R'",
     'oll-knight', 'difficile',
     "Cavalier — déplacement en L avec B move"),

    # ═══════════════════════════════════════════════════════════
    # AWKWARD (4) — cas inhabituels de la croix
    # ═══════════════════════════════════════════════════════════
    (21, "R U2 R' U' R U R' U' R U' R'",
     'oll-awkward', 'difficile',
     "Étrange — Anti-Sune étendu (arêtes orientées)"),

    (22, "R U2 R2 U' R2 U' R2 U2 R",
     'oll-awkward', 'difficile',
     "Étrange — Pi pattern (arêtes orientées)"),

    (23, "R2 D' R U2 R' D R U2 R",
     'oll-awkward', 'difficile',
     "Étrange — U pattern (arêtes orientées)"),

    (56, "f R U R' U' R U R' U' f'",
     'oll-awkward', 'difficile',
     "Étrange — cas inhabituel, double sexy move"),

    # ═══════════════════════════════════════════════════════════
    # T-SHAPE (2) — forme T
    # ═══════════════════════════════════════════════════════════
    (33, "R U R' U' R' F R F'",
     'oll-t-shape', 'facile',
     "Forme T — pattern T classique, algorithme court"),

    (43, "R' U' F' U F R",
     'oll-t-shape', 'facile',
     "Forme T — pattern T, version courte"),

    # ═══════════════════════════════════════════════════════════
    # C-SHAPE (2) — forme C
    # ═══════════════════════════════════════════════════════════
    (34, "R U R' U' B' R' F R F' B",
     'oll-c-shape', 'moyen',
     "Forme C — pattern en C, utilise B move"),

    (46, "R' U' R' F R F' U R",
     'oll-c-shape', 'moyen',
     "Forme C — pattern en C, version courte"),

    # ═══════════════════════════════════════════════════════════
    # W-SHAPE (2) — forme W
    # ═══════════════════════════════════════════════════════════
    (36, "R' U' R U' R' U R U R B' R' B",
     'oll-w-shape', 'difficile',
     "Forme W — pattern en W, utilise B move"),

    (38, "R U R' U R U' R' U' R' F R F'",
     'oll-w-shape', 'difficile',
     "Forme W — pattern en W, miroir"),
]

# ──────────────────────────────────────────────────────────────────────────────
# Population
# ──────────────────────────────────────────────────────────────────────────────

created_count = 0
updated_count = 0
errors = []

print("=" * 60)
print("Population des 57 cas OLL")
print("=" * 60)

for step_num, algorithm, category, difficulty, description in OLL_DATA:
    name = f'OLL {step_num:02d}'
    slug = f'oll-{step_num:02d}'

    try:
        cs, created = CubeState.objects.update_or_create(
            slug=slug,
            defaults={
                'name':         name,
                'algorithm':    algorithm,
                'category':     category,
                'difficulty':   difficulty,
                'description':  description,
                'method':       'cfop',
                'step_number':  step_num,
                'stickering':   'OLL',
                'json_state':   {},
                'hand_orientation': 'right',
            }
        )

        if created:
            created_count += 1
            print(f'  ✅ Créé    : {name} ({category})')
        else:
            updated_count += 1
            print(f'  🔄 Mis à jour : {name} ({category})')

    except Exception as e:
        errors.append((slug, str(e)))
        print(f'  ❌ Erreur  : {name} → {e}')

# ──────────────────────────────────────────────────────────────────────────────
# Résumé
# ──────────────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print(f"✅ Créés       : {created_count}")
print(f"🔄 Mis à jour  : {updated_count}")
print(f"❌ Erreurs     : {len(errors)}")
print()

# Vérification par catégorie
from collections import Counter
cats = Counter(
    CubeState.objects.filter(
        method='cfop', slug__startswith='oll-'
    ).values_list('category', flat=True)
)
print("Cas par catégorie :")
for cat, count in sorted(cats.items()):
    print(f"  {cat:<20} : {count}")

print()
total = CubeState.objects.filter(method='cfop', slug__startswith='oll-').count()
print(f"Total OLL dans la base : {total} / 57")
print("=" * 60)

if errors:
    print("\n⚠️  Erreurs détaillées :")
    for slug, err in errors:
        print(f"  {slug}: {err}")