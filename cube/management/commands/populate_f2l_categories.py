"""
Script pour pré-remplir les catégories et difficultés des cas F2L.

Usage:
    python manage.py shell < populate_f2l_categories.py
"""

from cube.models import CubeState

# Category and difficulty mapping for all F2L cases
F2L_MAPPING = {
    # Basic Cases (1-4)
    'f2l-01': {'category': 'basic', 'difficulty': 'facile'},
    'f2l-02': {'category': 'basic', 'difficulty': 'facile'},
    'f2l-03': {'category': 'basic', 'difficulty': 'facile'},
    'f2l-04': {'category': 'basic', 'difficulty': 'facile'},
    
    # Corner Right, Edge Right (5-8)
    'f2l-05': {'category': 'corner-right-edge-right', 'difficulty': 'moyen'},
    'f2l-06': {'category': 'corner-right-edge-right', 'difficulty': 'moyen'},
    'f2l-07': {'category': 'corner-right-edge-right', 'difficulty': 'moyen'},
    'f2l-08': {'category': 'corner-right-edge-right', 'difficulty': 'moyen'},
    
    # Corner Right, Edge Front (9-12)
    'f2l-09': {'category': 'corner-right-edge-front', 'difficulty': 'moyen'},
    'f2l-10': {'category': 'corner-right-edge-front', 'difficulty': 'moyen'},
    'f2l-11': {'category': 'corner-right-edge-front', 'difficulty': 'difficile'},
    'f2l-12': {'category': 'corner-right-edge-front', 'difficulty': 'moyen'},
    
    # Corner Left, Edge Left (13-16)
    'f2l-13': {'category': 'corner-left-edge-left', 'difficulty': 'moyen'},
    'f2l-14': {'category': 'corner-left-edge-left', 'difficulty': 'moyen'},
    'f2l-15': {'category': 'corner-left-edge-left', 'difficulty': 'moyen'},
    'f2l-16': {'category': 'corner-left-edge-left', 'difficulty': 'moyen'},
    
    # Corner Left, Edge Front (17-20)
    'f2l-17': {'category': 'corner-left-edge-front', 'difficulty': 'moyen'},
    'f2l-18': {'category': 'corner-left-edge-front', 'difficulty': 'moyen'},
    'f2l-19': {'category': 'corner-left-edge-front', 'difficulty': 'difficile'},
    'f2l-20': {'category': 'corner-left-edge-front', 'difficulty': 'moyen'},
    
    # Corner in Slot (21-28)
    'f2l-21': {'category': 'corner-in-slot', 'difficulty': 'facile'},
    'f2l-22': {'category': 'corner-in-slot', 'difficulty': 'facile'},
    'f2l-23': {'category': 'corner-in-slot', 'difficulty': 'moyen'},
    'f2l-24': {'category': 'corner-in-slot', 'difficulty': 'moyen'},
    'f2l-25': {'category': 'corner-in-slot', 'difficulty': 'moyen'},
    'f2l-26': {'category': 'corner-in-slot', 'difficulty': 'moyen'},
    'f2l-27': {'category': 'corner-in-slot', 'difficulty': 'moyen'},
    'f2l-28': {'category': 'corner-in-slot', 'difficulty': 'moyen'},
    
    # Edge in Slot (29-36)
    'f2l-29': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    'f2l-30': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    'f2l-31': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    'f2l-32': {'category': 'edge-in-slot', 'difficulty': 'facile'},
    'f2l-33': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    'f2l-34': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    'f2l-35': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    'f2l-36': {'category': 'edge-in-slot', 'difficulty': 'moyen'},
    
    # Both in Slot (37-41)
    'f2l-37': {'category': 'both-in-slot', 'difficulty': 'difficile'},
    'f2l-38': {'category': 'both-in-slot', 'difficulty': 'difficile'},
    'f2l-39': {'category': 'both-in-slot', 'difficulty': 'difficile'},
    'f2l-40': {'category': 'both-in-slot', 'difficulty': 'moyen'},
    'f2l-41': {'category': 'both-in-slot', 'difficulty': 'facile'},
}

print("=" * 70)
print("Pré-remplissage des catégories et difficultés F2L")
print("=" * 70)

updated_count = 0
skipped_count = 0
missing_count = 0

for slug, data in F2L_MAPPING.items():
    try:
        case = CubeState.objects.get(slug=slug)
        
        # Check if already has category
        if case.category and case.difficulty:
            print(f"⊘ Skip {slug} - Déjà configuré")
            skipped_count += 1
            continue
        
        # Update
        case.category = data['category']
        case.difficulty = data['difficulty']
        case.save()
        
        print(f"✓ {slug} - {case.name}")
        print(f"  category: {case.category}")
        print(f"  difficulty: {case.difficulty}")
        updated_count += 1
        
    except CubeState.DoesNotExist:
        print(f"✗ {slug} - Cas non trouvé dans la base de données")
        missing_count += 1

print("\n" + "=" * 70)
print("Résumé")
print("=" * 70)
print(f"Mis à jour: {updated_count}")
print(f"Ignorés:    {skipped_count}")
print(f"Manquants:  {missing_count}")
print(f"Total:      {len(F2L_MAPPING)}")
print("=" * 70)

if missing_count > 0:
    print("\n⚠️  Certains cas sont manquants. Crée-les d'abord avec create_f2l_cases.py")