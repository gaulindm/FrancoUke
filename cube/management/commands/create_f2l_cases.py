# Save this file as: cube/management/commands/create_f2l_cases.py
# 
# Directory structure should be:
# cube/
#   management/
#     __init__.py  (empty file)
#     commands/
#       __init__.py  (empty file)
#       create_f2l_cases.py  (this file)

from django.core.management.base import BaseCommand
from cube.models import CubeState


class Command(BaseCommand):
    help = 'Create all 41 F2L cases for CFOP method'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing cases instead of skipping them',
        )
        parser.add_argument(
            '--delete-all',
            action='store_true',
            help='Delete all existing F2L cases before creating new ones',
        )

    def handle(self, *args, **options):
        update_existing = options['update']
        delete_all = options['delete_all']
        
        # All 41 F2L cases
        f2l_cases = [
            # Group 1: Basic Cases
            {'slug': 'f2l-01', 'name': 'F2L #1 - Paire appariée droite', 'algorithm': 'R U R\'', 'description': 'Le coin et l\'arête sont déjà appariés, insertion simple à droite', 'difficulty': 'facile', 'step_number': 1},
            {'slug': 'f2l-02', 'name': 'F2L #2 - Paire appariée gauche', 'algorithm': 'L\' U\' L', 'description': 'Paire appariée, insertion par la gauche', 'difficulty': 'facile', 'step_number': 2},
            {'slug': 'f2l-03', 'name': 'F2L #3 - Paire appariée avec rotation U', 'algorithm': 'U R U\' R\'', 'description': 'La paire est formée mais mal orientée, ajustement puis insertion', 'difficulty': 'facile', 'step_number': 3},
            {'slug': 'f2l-04', 'name': 'F2L #4 - Paire appariée rotation U\'', 'algorithm': 'U\' L\' U L', 'description': 'Même principe que #3 mais côté gauche', 'difficulty': 'facile', 'step_number': 4},
            
            # Group 2: Corner Right, Edge Right
            {'slug': 'f2l-05', 'name': 'F2L #5 - Les deux blancs en haut', 'algorithm': 'U R U\' R\' U\' F\' U F', 'description': 'Le coin et l\'arête sont séparés, blancs visibles en haut', 'difficulty': 'moyen', 'step_number': 5},
            {'slug': 'f2l-06', 'name': 'F2L #6 - Coin blanc haut, arête blanche côté', 'algorithm': 'U\' R U R\' U R U R\'', 'description': 'Formation et insertion en une séquence', 'difficulty': 'moyen', 'step_number': 6},
            {'slug': 'f2l-07', 'name': 'F2L #7 - Coin blanc côté, arête blanche haut', 'algorithm': 'U\' R U\' R\' U R U R\'', 'description': 'Cas opposé au #6', 'difficulty': 'moyen', 'step_number': 7},
            {'slug': 'f2l-08', 'name': 'F2L #8 - Les deux blancs sur le côté', 'algorithm': 'R U\' R\' U R U\' R\'', 'description': 'Les blancs se font face sur le côté', 'difficulty': 'moyen', 'step_number': 8},
            
            # Group 3: Corner Right, Edge Front
            {'slug': 'f2l-09', 'name': 'F2L #9 - Coin à droite, arête devant (blancs haut)', 'algorithm': 'U F\' U\' F U\' R U R\'', 'description': 'Rapprocher et insérer', 'difficulty': 'moyen', 'step_number': 9},
            {'slug': 'f2l-10', 'name': 'F2L #10 - Coin blanc haut, arête blanche côté avant', 'algorithm': 'U F\' U F U R U R\'', 'description': 'Formation via face avant', 'difficulty': 'moyen', 'step_number': 10},
            {'slug': 'f2l-11', 'name': 'F2L #11 - Coin blanc côté, arête blanche haut avant', 'algorithm': 'R U R\' U\' U R U R\' U\' R U R\'', 'description': 'Séquence longue mais logique', 'difficulty': 'difficile', 'step_number': 11},
            {'slug': 'f2l-12', 'name': 'F2L #12 - Les deux blancs côté (perpendiculaires)', 'algorithm': 'R U\' R\' U\' F\' U F', 'description': 'Formation rapide et insertion', 'difficulty': 'moyen', 'step_number': 12},
            
            # Group 4: Corner Left, Edge Left
            {'slug': 'f2l-13', 'name': 'F2L #13 - Les deux blancs haut (gauche)', 'algorithm': 'U\' L\' U L U F U\' F\'', 'description': 'Miroir du cas #5', 'difficulty': 'moyen', 'step_number': 13},
            {'slug': 'f2l-14', 'name': 'F2L #14 - Coin blanc haut, arête côté (gauche)', 'algorithm': 'U L\' U\' L U\' L\' U\' L', 'description': 'Miroir du cas #6', 'difficulty': 'moyen', 'step_number': 14},
            {'slug': 'f2l-15', 'name': 'F2L #15 - Coin blanc côté, arête haut (gauche)', 'algorithm': 'U L\' U L U\' L\' U\' L', 'description': 'Miroir du cas #7', 'difficulty': 'moyen', 'step_number': 15},
            {'slug': 'f2l-16', 'name': 'F2L #16 - Les deux blancs côté (gauche)', 'algorithm': 'L\' U L U\' L\' U L', 'description': 'Miroir du cas #8', 'difficulty': 'moyen', 'step_number': 16},
            
            # Group 5: Corner Left, Edge Front
            {'slug': 'f2l-17', 'name': 'F2L #17 - Coin gauche, arête devant (blancs haut)', 'algorithm': 'U\' F U F\' U L\' U\' L', 'description': 'Miroir du cas #9', 'difficulty': 'moyen', 'step_number': 17},
            {'slug': 'f2l-18', 'name': 'F2L #18 - Coin blanc haut, arête côté avant (gauche)', 'algorithm': 'U\' F U\' F\' U\' L\' U\' L', 'description': 'Miroir du cas #10', 'difficulty': 'moyen', 'step_number': 18},
            {'slug': 'f2l-19', 'name': 'F2L #19 - Coin blanc côté, arête haut avant (gauche)', 'algorithm': 'L\' U\' L U U L\' U\' L U L\' U\' L', 'description': 'Miroir du cas #11', 'difficulty': 'difficile', 'step_number': 19},
            {'slug': 'f2l-20', 'name': 'F2L #20 - Les deux blancs côté perpendiculaires (gauche)', 'algorithm': 'L\' U L U F U\' F\'', 'description': 'Miroir du cas #12', 'difficulty': 'moyen', 'step_number': 20},
            
            # Group 6: Corner in Slot, Edge on Top
            {'slug': 'f2l-21', 'name': 'F2L #21 - Coin en bas blanc dessous, arête blanche haut', 'algorithm': 'R U\' R\' U R U\' R\'', 'description': 'Extraire, apparier, réinsérer (cas facile)', 'difficulty': 'facile', 'step_number': 21},
            {'slug': 'f2l-22', 'name': 'F2L #22 - Coin en bas, arête blanche côté', 'algorithm': 'R U R\' U\' R U R\'', 'description': 'Sexy move classique', 'difficulty': 'facile', 'step_number': 22},
            {'slug': 'f2l-23', 'name': 'F2L #23 - Coin blanc devant, arête blanche haut', 'algorithm': 'U\' R U\' R\' U2 R U\' R\'', 'description': 'Double rotation pour apparier', 'difficulty': 'moyen', 'step_number': 23},
            {'slug': 'f2l-24', 'name': 'F2L #24 - Coin blanc devant, arête blanche côté', 'algorithm': 'U F\' U F U\' R U R\'', 'description': 'Utilise la face avant pour formation', 'difficulty': 'moyen', 'step_number': 24},
            {'slug': 'f2l-25', 'name': 'F2L #25 - Coin blanc à droite, arête blanche haut', 'algorithm': 'U R U2 R\' U R U\' R\'', 'description': 'Formation avec double U', 'difficulty': 'moyen', 'step_number': 25},
            {'slug': 'f2l-26', 'name': 'F2L #26 - Coin blanc à droite, arête blanche côté', 'algorithm': 'R U\' R\' U\' F\' U F', 'description': 'Extraction et formation rapide', 'difficulty': 'moyen', 'step_number': 26},
            {'slug': 'f2l-27', 'name': 'F2L #27 - Coin blanc devant, arête haut (gauche)', 'algorithm': 'U L\' U L U2 L\' U L', 'description': 'Miroir du cas #23', 'difficulty': 'moyen', 'step_number': 27},
            {'slug': 'f2l-28', 'name': 'F2L #28 - Coin blanc gauche, arête blanche côté', 'algorithm': 'L\' U L U F U\' F\'', 'description': 'Miroir du cas #26', 'difficulty': 'moyen', 'step_number': 28},
            
            # Group 7: Edge in Slot, Corner on Top
            {'slug': 'f2l-29', 'name': 'F2L #29 - Arête en bas blanche dessous, coin blanc haut', 'algorithm': 'U\' R U R\' U R U R\'', 'description': 'Extraire l\'arête, apparier, insérer', 'difficulty': 'moyen', 'step_number': 29},
            {'slug': 'f2l-30', 'name': 'F2L #30 - Arête en bas, coin blanc côté', 'algorithm': 'U\' R U\' R\' U R U R\'', 'description': 'Variation du cas #29', 'difficulty': 'moyen', 'step_number': 30},
            {'slug': 'f2l-31', 'name': 'F2L #31 - Arête blanche droite, coin blanc haut', 'algorithm': 'R U\' R\' U2 F\' U\' F', 'description': 'Extraction et formation par avant', 'difficulty': 'moyen', 'step_number': 31},
            {'slug': 'f2l-32', 'name': 'F2L #32 - Arête blanche droite, coin blanc côté droit', 'algorithm': 'R U R\' U\' R U R\'', 'description': 'Formation directe', 'difficulty': 'facile', 'step_number': 32},
            {'slug': 'f2l-33', 'name': 'F2L #33 - Arête blanche devant, coin blanc haut', 'algorithm': 'U R U2 R\' U F\' U\' F', 'description': 'Double rotation pour synchroniser', 'difficulty': 'moyen', 'step_number': 33},
            {'slug': 'f2l-34', 'name': 'F2L #34 - Arête blanche devant, coin blanc côté', 'algorithm': 'U F\' U\' F U\' R U R\'', 'description': 'Formation via face avant', 'difficulty': 'moyen', 'step_number': 34},
            {'slug': 'f2l-35', 'name': 'F2L #35 - Arête blanche gauche, coin blanc haut', 'algorithm': 'L\' U L U2 F U F\'', 'description': 'Miroir du cas #31', 'difficulty': 'moyen', 'step_number': 35},
            {'slug': 'f2l-36', 'name': 'F2L #36 - Arête blanche devant, coin côté gauche', 'algorithm': 'U\' F U F\' U L\' U\' L', 'description': 'Miroir du cas #34', 'difficulty': 'moyen', 'step_number': 36},
            
            # Group 8: Both in Slot (Wrong)
            {'slug': 'f2l-37', 'name': 'F2L #37 - Les deux inversés dans le slot', 'algorithm': 'R U\' R\' U\' R U R\' U2 R U\' R\'', 'description': 'Extraction et réinsertion complète', 'difficulty': 'difficile', 'step_number': 37},
            {'slug': 'f2l-38', 'name': 'F2L #38 - Coin correct, arête inversée', 'algorithm': 'R U R\' U\' R U\' R\' U2 F\' U\' F', 'description': 'Correction de l\'arête seulement', 'difficulty': 'difficile', 'step_number': 38},
            {'slug': 'f2l-39', 'name': 'F2L #39 - Arête correcte, coin inversé', 'algorithm': 'R U\' R\' U R U2 R\' U R U\' R\'', 'description': 'Correction du coin seulement', 'difficulty': 'difficile', 'step_number': 39},
            {'slug': 'f2l-40', 'name': 'F2L #40 - Les deux dans le mauvais slot', 'algorithm': 'R U\' R\' U\' F\' U F', 'description': 'Extraction rapide et réinsertion', 'difficulty': 'moyen', 'step_number': 40},
            {'slug': 'f2l-41', 'name': 'F2L #41 - Paire déjà résolue', 'algorithm': '', 'description': 'Cas de référence - la paire est déjà complète et correcte', 'difficulty': 'facile', 'step_number': 41},
        ]
        
        # Delete all existing F2L cases if requested
        if delete_all:
            self.stdout.write(self.style.WARNING('Deleting all existing F2L cases...'))
            deleted_count = CubeState.objects.filter(slug__startswith='f2l-').delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} F2L cases'))
        
        # Create or update cases
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('Creating F2L Cases'))
        self.stdout.write('=' * 70)
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for case_data in f2l_cases:
            slug = case_data['slug']
            existing = CubeState.objects.filter(slug=slug).first()
            
            if existing:
                if update_existing:
                    # Update existing
                    for key, value in case_data.items():
                        if key != 'slug':
                            setattr(existing, key, value)
                    existing.method = 'cfop'
                    existing.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated: {slug} - {case_data["name"]}'))
                    updated_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'⊘ Skipped: {slug} - {case_data["name"]} (already exists)'))
                    skipped_count += 1
            else:
                # Create new
                CubeState.objects.create(
                    slug=slug,
                    name=case_data['name'],
                    algorithm=case_data['algorithm'],
                    description=case_data['description'],
                    step_number=case_data['step_number'],
                    method='cfop',
                    json_state={},
                    json_highlight=None,
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {slug} - {case_data["name"]}'))
                created_count += 1
        
        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'Created: {created_count}')
        self.stdout.write(f'Updated: {updated_count}')
        self.stdout.write(f'Skipped: {skipped_count}')
        self.stdout.write(f'Total:   {len(f2l_cases)}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  Remember: You still need to set the json_state for each case in Django Admin!'))
        self.stdout.write('=' * 70)