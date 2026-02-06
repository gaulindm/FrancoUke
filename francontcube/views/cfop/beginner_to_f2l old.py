"""
Bridge page: From Beginner Method to F2L.

Shows students how the second layer algorithm they already know
is actually F2L in disguise!
"""

from django.urls import reverse
from ..base import StepView


class BeginnerToF2LView(StepView):
    """
    Educational bridge page showing how beginner second layer = F2L.
    
    This page helps students realize they already know F2L concepts:
    - U' F' U F (4 moves) = Pairing the corner and edge
    - U R U' R' (4 moves) = Inserting the pair
    """
    
    template_name = "francontcube/methods/cfop/beginner_to_f2l.html"
    method_name = "CFOP"
    step_name = "De Débutant à F2L"
    step_icon = "lightbulb-fill"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'case_right_state': 'beg-second-layer-case-right',
        # You can add more cube states as you create them:
        # 'case_left_state': 'beg-second-layer-case-left',
        # 'pairing_demo_state': 'f2l-pairing-demo',
        # 'insertion_demo_state': 'f2l-insertion-demo',
    }
    
    def get_context_data(self, **kwargs):
        """Add custom context for this bridge page."""
        context = super().get_context_data(**kwargs)
        
        # The revelation: beginner algorithm = F2L
        context['beginner_algorithm'] = {
            'full': "U' F' U F U R U' R'",
            'part1': {
                'moves': "U' F' U F",
                'name': 'Formation de la Paire',
                'description': 'Ces 4 premiers mouvements créent la paire coin-arête',
                'what_happens': 'Le coin et l\'arête se retrouvent ensemble, prêts à être insérés',
            },
            'part2': {
                'moves': "U R U' R'",
                'name': 'Insertion (Sexy Move)',
                'description': 'Ces 4 derniers mouvements insèrent la paire dans son slot',
                'what_happens': 'La paire descend à sa place dans la deuxième couche',
            },
        }
        
        # Different cases students know from beginner method
        context['second_layer_cases'] = [
            {
                'name': 'Cas Gauche (arête à gauche)',
                'beginner_alg': "U' L' U L U F U' F'",
                'description': 'Version miroir pour l\'arête qui va à gauche',
                'pairing': "U' L' U L",
                'insertion': "U F U' F'",
                'f2l_equivalent': 'F2L #5 ou similaire',
            },
            {
                'name': 'Cas Droite (arête à droite)',
                'beginner_alg': "U' F' U F U R U' R'",
                'description': 'L\'algorithme classique pour l\'arête qui va à droite',
                'pairing': "U' F' U F",
                'insertion': "U R U' R'",
                'f2l_equivalent': 'F2L #5 ou similaire',
            },
        ]
        
        # Key insights for students
        context['revelations'] = [
            {
                'icon': 'bi-lightbulb-fill',
                'title': 'Vous Connaissez Déjà du F2L!',
                'desc': 'L\'algorithme de la deuxième couche que vous utilisez depuis le début est en fait du F2L déguisé.',
                'color': 'success',
            },
            {
                'icon': 'bi-puzzle',
                'title': 'Deux Parties Distinctes',
                'desc': 'Les 4 premiers mouvements forment la paire (pairing), les 4 derniers l\'insèrent (insertion).',
                'color': 'primary',
            },
            {
                'icon': 'bi-arrow-repeat',
                'title': 'Le Sexy Move',
                'desc': 'U R U\' R\' est l\'insertion la plus commune en F2L. Vous le faites déjà 4 fois par résolution!',
                'color': 'info',
            },
            {
                'icon': 'bi-graph-up',
                'title': 'Progression Naturelle',
                'desc': 'F2L, c\'est comprendre POURQUOI ça marche, pas juste mémoriser. Vous avez déjà l\'intuition!',
                'color': 'warning',
            },
        ]
        
        # Comparison: Beginner vs F2L approach
        context['comparison'] = {
            'beginner': {
                'name': 'Méthode Débutant',
                'steps': [
                    'Croix blanche (4 arêtes)',
                    'Coins blancs (4 coins)',
                    'Deuxième couche (4 arêtes) ← VOUS ÊTES ICI',
                    'Croix jaune',
                    'Face jaune',
                    'Permutation coins',
                    'Permutation arêtes',
                ],
                'total_steps': 7,
                'second_layer': {
                    'description': 'Vous résolvez 4 arêtes une par une avec l\'algorithme U\' F\' U F U R U\' R\'',
                    'repetitions': 4,
                    'mindset': 'Algorithme mémorisé sans comprendre le pourquoi',
                },
            },
            'f2l': {
                'name': 'CFOP avec F2L',
                'steps': [
                    'Croix blanche (4 arêtes)',
                    'F2L (4 paires coin+arête) ← LA MÊME CHOSE!',
                    'OLL (orientation dernière couche)',
                    'PLL (permutation dernière couche)',
                ],
                'total_steps': 4,
                'second_layer': {
                    'description': 'Vous résolvez 4 paires (coin+arête ensemble) de façon intuitive',
                    'repetitions': 4,
                    'mindset': 'Comprendre comment les pièces interagissent',
                },
            },
        }
        
        # Next steps for learning F2L
        context['learning_path'] = [
            {
                'step': 1,
                'title': 'Réalisez que Vous Savez Déjà',
                'desc': 'L\'algorithme U\' F\' U F U R U\' R\' est du F2L. Vous le faites 4 fois par cube.',
                'action': 'Regardez attentivement : les 4 premiers mouvements créent la paire!',
            },
            {
                'step': 2,
                'title': 'Séparez Mentalement en Deux Parties',
                'desc': 'Pairing (U\' F\' U F) puis Insertion (U R U\' R\'). Ce sont deux actions distinctes.',
                'action': 'Faites une pause entre les deux parties pour voir la paire formée en haut.',
            },
            {
                'step': 3,
                'title': 'Apprenez les 4 Cas de Base',
                'desc': 'Il existe 4 façons simples d\'insérer une paire déjà formée.',
                'action': 'Commencez par F2L #1-4 : juste insérer des paires déjà faites.',
            },
            {
                'step': 4,
                'title': 'Découvrez les Autres Façons de Pairer',
                'desc': 'U\' F\' U F n\'est qu\'UNE façon de former une paire. Il y en a 40 autres!',
                'action': 'Explorez F2L #5-8 : d\'autres techniques de pairing.',
            },
            {
                'step': 5,
                'title': 'Pratiquez Intuitivement',
                'desc': 'F2L n\'est pas 41 algorithmes à mémoriser, c\'est COMPRENDRE comment pairer et insérer.',
                'action': 'Résolvez quelques paires lentement en PENSANT à ce que vous faites.',
            },
        ]
        
        # Interactive breakdown visualization
        context['algorithm_breakdown'] = {
            'title': 'Décorticage de l\'Algorithme Débutant',
            'full_alg': "U' F' U F U R U' R'",
            'analysis': [
                {
                    'move': "U'",
                    'purpose': 'Setup',
                    'what_happens': 'Positionne l\'arête',
                    'part': 'pairing',
                },
                {
                    'move': "F'",
                    'purpose': 'Extrait le coin',
                    'what_happens': 'Sort le coin blanc du slot',
                    'part': 'pairing',
                },
                {
                    'move': "U",
                    'purpose': 'Rapproche',
                    'what_happens': 'Rapproche le coin et l\'arête',
                    'part': 'pairing',
                },
                {
                    'move': "F",
                    'purpose': 'Forme la paire',
                    'what_happens': 'Le coin et l\'arête sont maintenant ensemble!',
                    'part': 'pairing',
                },
                {
                    'move': "U",
                    'purpose': 'Setup insertion',
                    'what_happens': 'Positionne la paire au-dessus du slot vide',
                    'part': 'insertion',
                },
                {
                    'move': "R",
                    'purpose': 'Ouvre le slot',
                    'what_happens': 'Crée de l\'espace pour la paire',
                    'part': 'insertion',
                },
                {
                    'move': "U'",
                    'purpose': 'Descend la paire',
                    'what_happens': 'La paire entre dans le slot',
                    'part': 'insertion',
                },
                {
                    'move': "R'",
                    'purpose': 'Ferme le slot',
                    'what_happens': 'La paire est insérée! Deuxième couche résolue.',
                    'part': 'insertion',
                },
            ],
        }
        
        # Practical exercise
        context['exercise'] = {
            'title': 'Exercice Pratique : Voir la Paire',
            'steps': [
                'Résolvez la croix blanche et les 4 coins blancs (méthode débutant)',
                'Trouvez une arête de la deuxième couche',
                'Faites SEULEMENT les 4 premiers mouvements : U\' F\' U F',
                'ARRÊTEZ-VOUS et regardez le cube',
                'Vous devriez voir le coin ET l\'arête ensemble en haut!',
                'Maintenant faites U R U\' R\' pour les insérer',
                'Répétez avec les 3 autres arêtes',
            ],
            'goal': 'Réaliser physiquement que vous créez des paires depuis le début!',
        }
        
        return context


# Export the view function for URL routing
beginner_to_f2l_bridge = BeginnerToF2LView.as_view()