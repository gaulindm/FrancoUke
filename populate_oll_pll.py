# populate_oll_pll.py
# Run with: python manage.py shell < populate_oll_pll.py

from cube.models import CubeState

# OLL Cases (Orientation of Last Layer)
oll_cases = [
    # OLL Cross (1 case)
    {
        'name': 'OLL #1 - Already Oriented',
        'slug': 'oll-01',
        'algorithm': '',
        'description': 'Tous les stickers du dessus sont déjà jaunes',
        'step_number': 1,
        'method': 'cfop',
        'category': 'oll-cross',
        'difficulty': 'facile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}  # TODO: fill with actual state
    },
    
    # OLL Dot (8 cases) - Only center is yellow
    {
        'name': 'OLL #2 - Dot (Sune)',
        'slug': 'oll-02',
        'algorithm': "R U R' U R U2 R'",
        'description': 'Dot pattern - Position classique Sune',
        'step_number': 2,
        'method': 'cfop',
        'category': 'oll-dot',
        'difficulty': 'facile',
        'roofpig_setup': "R U R' U R U2 R' U",
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg speed:1.5',
        'json_state': {}
    },
    {
        'name': 'OLL #3 - Dot (Anti-Sune)',
        'slug': 'oll-03',
        'algorithm': "L' U' L U' L' U2 L",
        'description': 'Dot pattern - Miroir de Sune',
        'step_number': 3,
        'method': 'cfop',
        'category': 'oll-dot',
        'difficulty': 'facile',
        'roofpig_setup': "L' U' L U' L' U2 L U'",
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg speed:1.5',
        'json_state': {}
    },
    
    # OLL Line (8 cases)
    {
        'name': 'OLL #51 - Line',
        'slug': 'oll-51',
        'algorithm': "F U R U' R' F'",
        'description': 'Ligne horizontale - Cas le plus commun',
        'step_number': 51,
        'method': 'cfop',
        'category': 'oll-line',
        'difficulty': 'facile',
        'roofpig_setup': "F U R U' R' F' U",
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'OLL #52 - Line',
        'slug': 'oll-52',
        'algorithm': "R U R' U R U' R' U R U2 R'",
        'description': 'Ligne avec coins inversés',
        'step_number': 52,
        'method': 'cfop',
        'category': 'oll-line',
        'difficulty': 'moyen',
        'roofpig_setup': "R U R' U R U' R' U R U2 R' U",
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    
    # OLL L-Shape (6 cases)
    {
        'name': 'OLL #47 - L-Shape',
        'slug': 'oll-47',
        'algorithm': "F' L' U' L U L' U' L U F",
        'description': 'Forme L dans le coin',
        'step_number': 47,
        'method': 'cfop',
        'category': 'oll-l-shape',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'OLL #48 - L-Shape',
        'slug': 'oll-48',
        'algorithm': "F R U R' U' R U R' U' F'",
        'description': 'Forme L miroir',
        'step_number': 48,
        'method': 'cfop',
        'category': 'oll-l-shape',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    
    # OLL Square (4 cases)
    {
        'name': 'OLL #5 - Square',
        'slug': 'oll-05',
        'algorithm': "r U2 R' U' R U' r'",
        'description': 'Carré dans le coin - r = rotation large',
        'step_number': 5,
        'method': 'cfop',
        'category': 'oll-square',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'OLL #6 - Square',
        'slug': 'oll-06',
        'algorithm': "l' U2 L U L' U l",
        'description': 'Carré miroir - l = rotation large',
        'step_number': 6,
        'method': 'cfop',
        'category': 'oll-square',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U-',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
]

# PLL Cases (Permutation of Last Layer)
pll_cases = [
    # PLL Adjacent Swaps
    {
        'name': 'PLL - Aa Perm',
        'slug': 'pll-aa',
        'algorithm': "x R' U R' D2 R U' R' D2 R2 x'",
        'description': 'Échange de coins adjacents (sens horaire)',
        'step_number': 1,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Ab Perm',
        'slug': 'pll-ab',
        'algorithm': "x R2 D2 R U R' D2 R U' R x'",
        'description': 'Échange de coins adjacents (sens antihoraire)',
        'step_number': 2,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - T Perm',
        'slug': 'pll-t',
        'algorithm': "R U R' U' R' F R2 U' R' U' R U R' F'",
        'description': 'Échange de deux arêtes adjacentes - Très commun',
        'step_number': 3,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'facile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - Ja Perm',
        'slug': 'pll-ja',
        'algorithm': "x R2 F R F' R U2 r' U r U2 x'",
        'description': 'Échange adjacent - Un coin et deux arêtes',
        'step_number': 4,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - Jb Perm',
        'slug': 'pll-jb',
        'algorithm': "R U R' F' R U R' U' R' F R2 U' R'",
        'description': 'Échange adjacent miroir de Ja',
        'step_number': 5,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - F Perm',
        'slug': 'pll-f',
        'algorithm': "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
        'description': 'Échange adjacent complexe',
        'step_number': 6,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Ra Perm',
        'slug': 'pll-ra',
        'algorithm': "R U R' F' R U2 R' U2 R' F R U R U2 R'",
        'description': 'Échange adjacent - R family',
        'step_number': 7,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - Rb Perm',
        'slug': 'pll-rb',
        'algorithm': "R' U2 R U2 R' F R U R' U' R' F' R2",
        'description': 'Échange adjacent - R family miroir',
        'step_number': 8,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - Ga Perm',
        'slug': 'pll-ga',
        'algorithm': "R2 U R' U R' U' R U' R2 U' D R' U R D'",
        'description': 'Échange adjacent - G family',
        'step_number': 9,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Gb Perm',
        'slug': 'pll-gb',
        'algorithm': "R' U' R U D' R2 U R' U R U' R U' R2 D",
        'description': 'Échange adjacent - G family',
        'step_number': 10,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Gc Perm',
        'slug': 'pll-gc',
        'algorithm': "R2 U' R U' R U R' U R2 U D' R U' R' D",
        'description': 'Échange adjacent - G family',
        'step_number': 11,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Gd Perm',
        'slug': 'pll-gd',
        'algorithm': "R U R' U' D R2 U' R U' R' U R' U R2 D'",
        'description': 'Échange adjacent - G family',
        'step_number': 12,
        'method': 'cfop',
        'category': 'pll-adjacent-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    
    # PLL Diagonal Swaps
    {
        'name': 'PLL - Y Perm',
        'slug': 'pll-y',
        'algorithm': "F R U' R' U' R U R' F' R U R' U' R' F R F'",
        'description': 'Échange diagonal de coins',
        'step_number': 13,
        'method': 'cfop',
        'category': 'pll-diagonal-swap',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - V Perm',
        'slug': 'pll-v',
        'algorithm': "R' U R' U' y R' F' R2 U' R' U R' F R F",
        'description': 'Échange diagonal - V shape',
        'step_number': 14,
        'method': 'cfop',
        'category': 'pll-diagonal-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Na Perm',
        'slug': 'pll-na',
        'algorithm': "R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R'",
        'description': 'Échange diagonal - N family',
        'step_number': 15,
        'method': 'cfop',
        'category': 'pll-diagonal-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    {
        'name': 'PLL - Nb Perm',
        'slug': 'pll-nb',
        'algorithm': "R' U R U' R' F' U' F R U R' F R' F' R U' R",
        'description': 'Échange diagonal - N family miroir',
        'step_number': 16,
        'method': 'cfop',
        'category': 'pll-diagonal-swap',
        'difficulty': 'difficile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:0.75',
        'json_state': {}
    },
    
    # PLL Edges Only
    {
        'name': 'PLL - Ua Perm',
        'slug': 'pll-ua',
        'algorithm': "R U' R U R U R U' R' U' R2",
        'description': 'Cycle 3 arêtes (sens horaire)',
        'step_number': 17,
        'method': 'cfop',
        'category': 'pll-edges-only',
        'difficulty': 'facile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:1.5',
        'json_state': {}
    },
    {
        'name': 'PLL - Ub Perm',
        'slug': 'pll-ub',
        'algorithm': "R2 U R U R' U' R' U' R' U R'",
        'description': 'Cycle 3 arêtes (sens antihoraire)',
        'step_number': 18,
        'method': 'cfop',
        'category': 'pll-edges-only',
        'difficulty': 'facile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg speed:1.5',
        'json_state': {}
    },
    {
        'name': 'PLL - H Perm',
        'slug': 'pll-h',
        'algorithm': "M2 U M2 U2 M2 U M2",
        'description': 'Échange de 2 paires d\'arêtes opposées',
        'step_number': 19,
        'method': 'cfop',
        'category': 'pll-edges-only',
        'difficulty': 'facile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    {
        'name': 'PLL - Z Perm',
        'slug': 'pll-z',
        'algorithm': "M' U M2 U M2 U M' U2 M2",
        'description': 'Échange de 2 paires d\'arêtes adjacentes',
        'step_number': 20,
        'method': 'cfop',
        'category': 'pll-edges-only',
        'difficulty': 'moyen',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
    
    # Solved
    {
        'name': 'PLL - Solved',
        'slug': 'pll-solved',
        'algorithm': '',
        'description': 'Cube résolu - Aucun PLL nécessaire',
        'step_number': 21,
        'method': 'cfop',
        'category': 'pll-solved',
        'difficulty': 'facile',
        'roofpig_setup': '',
        'roofpig_colored': 'U*',
        'roofpig_flags': 'showalg',
        'json_state': {}
    },
]

# Create or update OLL cases
print("Creating OLL cases...")
for case_data in oll_cases:
    case, created = CubeState.objects.update_or_create(
        slug=case_data['slug'],
        defaults=case_data
    )
    status = "Created" if created else "Updated"
    print(f"  {status}: {case.name}")

# Create or update PLL cases
print("\nCreating PLL cases...")
for case_data in pll_cases:
    case, created = CubeState.objects.update_or_create(
        slug=case_data['slug'],
        defaults=case_data
    )
    status = "Created" if created else "Updated"
    print(f"  {status}: {case.name}")

# Statistics
oll_count = CubeState.objects.filter(method='cfop', slug__startswith='oll-').count()
pll_count = CubeState.objects.filter(method='cfop', slug__startswith='pll-').count()

print(f"\n✅ Done!")
print(f"   OLL cases in database: {oll_count}")
print(f"   PLL cases in database: {pll_count}")
print(f"\nNote: You'll need to fill in the json_state for each case.")
print(f"Run the server and visit /cube/oll/ and /cube/pll/ to see them!")