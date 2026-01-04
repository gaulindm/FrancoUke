# training/management/commands/populate_training.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import Q
from training.models import Algorithm

class Command(BaseCommand):
    help = 'Populate training algorithms from F2L cases or create test algorithms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-data',
            action='store_true',
            help='Create test algorithms instead of importing from cube app',
        )

    def handle(self, *args, **options):
        if options['test_data']:
            self.create_test_algorithms()
        else:
            self.import_from_f2l()

    def import_from_f2l(self):
        """Import algorithms from CubeState F2L cases"""
        self.stdout.write("Importation depuis les cas F2L...")
        
        # Vérifier si l'app cube existe
        try:
            CubeState = apps.get_model('cube', 'CubeState')
        except LookupError:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  L'app 'cube' n'est pas installée ou CubeState n'existe pas."
                )
            )
            self.stdout.write("Utilise --test-data pour créer des algorithmes de test.")
            return
        
        # Récupérer tous les cas F2L (filtrer par method='cfop' et category contenant 'f2l' ou slug commençant par 'f2l')
        f2l_cases = CubeState.objects.filter(
            method='cfop'
        ).filter(
            Q(category__icontains='f2l') | Q(slug__startswith='f2l-')
        )
        
        if not f2l_cases.exists():
            self.stdout.write(
                self.style.WARNING("⚠️  Aucun cas F2L trouvé dans la base de données.")
            )
            self.stdout.write("Utilise --test-data pour créer des algorithmes de test.")
            return
        
        created_count = 0
        updated_count = 0
        
        # Mapper les difficultés
        difficulty_map = {
            'facile': 'apprenti',
            'moyen': 'confirme',
            'difficile': 'maitre'
        }
        
        # Mapper le nombre de répétitions
        reps_map = {
            'facile': 4,
            'moyen': 6,
            'difficile': 8
        }
        
        for case in f2l_cases:
            difficulty = difficulty_map.get(case.difficulty, 'confirme')
            repetitions = reps_map.get(case.difficulty, 6)
            
            # Créer ou mettre à jour l'algorithme
            algo, created = Algorithm.objects.update_or_create(
                slug=case.slug,
                defaults={
                    'name': case.name,
                    'notation': case.algorithm,
                    'repetitions': repetitions,
                    'difficulty': difficulty,
                    'description': case.description or f"Cas F2L #{case.step_number}",
                    'category': case.category or 'f2l'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Créé: {algo.name} ({algo.notation})')
                )
            else:
                updated_count += 1
                self.stdout.write(f'  Mis à jour: {algo.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Terminé! {created_count} algorithmes créés, {updated_count} mis à jour.'
            )
        )

    def create_test_algorithms(self):
        """Create test algorithms for development"""
        self.stdout.write("Création d'algorithmes de test...")
        
        test_algorithms = [
            # Cas basiques
            {
                'name': 'F2L #1 - Paire Simple Droite',
                'slug': 'f2l-01-test',
                'notation': 'R U R\'',
                'difficulty': 'apprenti',
                'repetitions': 4,
                'category': 'basic',
                'description': 'Insertion simple d\'une paire déjà formée à droite'
            },
            {
                'name': 'F2L #2 - Paire Simple Gauche',
                'slug': 'f2l-02-test',
                'notation': 'L\' U\' L',
                'difficulty': 'apprenti',
                'repetitions': 4,
                'category': 'basic',
                'description': 'Insertion simple d\'une paire déjà formée à gauche'
            },
            {
                'name': 'F2L #3 - Avec U',
                'slug': 'f2l-03-test',
                'notation': 'U R U\' R\'',
                'difficulty': 'apprenti',
                'repetitions': 4,
                'category': 'basic',
                'description': 'Paire formée avec setup U'
            },
            {
                'name': 'F2L #4 - Avec U\'',
                'slug': 'f2l-04-test',
                'notation': 'U\' L\' U L',
                'difficulty': 'apprenti',
                'repetitions': 4,
                'category': 'basic',
                'description': 'Paire formée avec setup U\''
            },
            
            # Cas moyens
            {
                'name': 'F2L #5 - Blancs en haut',
                'slug': 'f2l-05-test',
                'notation': 'U R U\' R\' U\' F\' U F',
                'difficulty': 'confirme',
                'repetitions': 6,
                'category': 'corner-right-edge-right',
                'description': 'Coin et arête avec blanc visible en haut'
            },
            {
                'name': 'F2L #22 - Sexy Move',
                'slug': 'f2l-22-test',
                'notation': 'R U R\' U\' R U R\'',
                'difficulty': 'confirme',
                'repetitions': 6,
                'category': 'corner-in-slot',
                'description': 'Le classique sexy move pour F2L'
            },
            
            # Cas difficiles
            {
                'name': 'F2L #37 - Cas Difficile',
                'slug': 'f2l-37-test',
                'notation': 'R U\' R\' U\' R U R\' U2 R U\' R\'',
                'difficulty': 'maitre',
                'repetitions': 8,
                'category': 'both-in-slot',
                'description': 'Les deux pièces inversées dans le slot'
            },
            
            # Algorithmes supplémentaires pour la variété
            {
                'name': 'OLL #1 - Croix',
                'slug': 'oll-01-test',
                'notation': 'F R U R\' U\' F\'',
                'difficulty': 'confirme',
                'repetitions': 5,
                'category': 'oll',
                'description': 'Forme une croix sur la face supérieure'
            },
            {
                'name': 'PLL #1 - T-Perm',
                'slug': 'pll-t-test',
                'notation': 'R U R\' U\' R\' F R2 U\' R\' U\' R U R\' F\'',
                'difficulty': 'speedcube',
                'repetitions': 6,
                'category': 'pll',
                'description': 'Permutation T classique'
            },
            {
                'name': 'PLL #2 - J-Perm',
                'slug': 'pll-j-test',
                'notation': 'R U R\' F\' R U R\' U\' R\' F R2 U\' R\'',
                'difficulty': 'speedcube',
                'repetitions': 6,
                'category': 'pll',
                'description': 'Permutation J'
            },
        ]
        
        created_count = 0
        
        for algo_data in test_algorithms:
            algo, created = Algorithm.objects.get_or_create(
                slug=algo_data['slug'],
                defaults=algo_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Créé: {algo.name} ({algo.notation})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Existe déjà: {algo.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Terminé! {created_count} algorithmes de test créés.'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Ce sont des données de test. Pour importer les vrais cas F2L,'
            )
        )
        self.stdout.write('    exécute: python manage.py populate_training')