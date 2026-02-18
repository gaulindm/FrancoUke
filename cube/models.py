# Add these fields to your CubeState model in cube/models.py

from django.db import models
from django.utils.text import slugify
from django.utils.safestring import mark_safe


class CubeState(models.Model):
    METHOD_CHOICES = [
        ("cubienewbie", "CubieNewbie"),
        ("beginner", "Beginner"),
        ("cfop", "CFOP"),
        ("roux", "Roux"),
        ("zz", "ZZ"),
    ]
    
    DIFFICULTY_CHOICES = [
        ('facile', 'Facile'),
        ('moyen', 'Moyen'),
        ('difficile', 'Difficile'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    json_state = models.JSONField()
    json_highlight = models.JSONField(
        blank=True,
        null=True,
        help_text="Instructional highlighting per sticker"
    )
    algorithm = models.TextField(blank=True)
    description = models.TextField(blank=True)
    step_number = models.PositiveIntegerField(default=1)
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default="beginner",
    )
    # Nouveau champ
    hand_orientation = models.CharField(
        max_length=10,
        choices=[
            ('right', 'Main Droite'),
            ('left', 'Main Gauche'),
        ],
        default='right',
        help_text="Quelle main fait les mouvements (détermine l'orientation du cube)"
    )
    
    # Category and difficulty
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Category/group for filtering (e.g., 'basic', 'corner-right-edge-right')"
    )
    difficulty = models.CharField(
        max_length=20,
        blank=True,
        choices=DIFFICULTY_CHOICES,
        help_text="Difficulty level of the case"
    )
    
    # Roofpig configuration fields
    roofpig_setup = models.TextField(
        blank=True,
        help_text="Roofpig setup moves to position the cube (ex: 'R U R' F' U' F')"
    )
    roofpig_colored = models.TextField(
        blank=True,
        help_text="Roofpig colored pieces to highlight (ex: 'U- D- L* Ufr Ufl')"
    )
    roofpig_flags = models.CharField(
        max_length=200,
        blank=True,
        default='showalg',
        help_text="Roofpig display flags (ex: 'showalg speed:2')"
    )

    def get_algorithm_svg(self):
        """
        Generate SVG icons from algorithm string.
        Supports grouping notation:
          ( )  → group-paren  → blue
          [ ]  → group-bracket → orange
        Moves outside groups render in the default black.

        Example: (R U' R') (U' R U R') [U2 R U' R']
        """
        if not self.algorithm or self.algorithm.strip() == '':
            return ''

        import re

        def move_to_svg(move, extra_class=''):
            svg_id = move.replace("'", "-prime")
            css = f'move-icon {extra_class}'.strip()
            return f'<svg class="{css}" aria-label="{move}"><use href="#{svg_id}"/></svg>'

        # Tokenise: split into paren groups, bracket groups, and bare moves.
        # We walk char by char to handle spaces inside groups gracefully.
        alg = self.algorithm.strip()

        # Build a flat list of tokens:
        #   {'type': 'group-paren'|'group-bracket'|'move', 'moves': [...]}
        tokens = []
        i = 0
        while i < len(alg):
            ch = alg[i]

            if ch == '(':
                # Collect until matching ')'
                depth = 1
                j = i + 1
                while j < len(alg) and depth:
                    if alg[j] == '(':
                        depth += 1
                    elif alg[j] == ')':
                        depth -= 1
                    j += 1
                inner = alg[i+1:j-1].strip()
                moves = [m for m in inner.split() if m]
                tokens.append({'type': 'group-paren', 'moves': moves})
                i = j

            elif ch == '[':
                depth = 1
                j = i + 1
                while j < len(alg) and depth:
                    if alg[j] == '[':
                        depth += 1
                    elif alg[j] == ']':
                        depth -= 1
                    j += 1
                inner = alg[i+1:j-1].strip()
                moves = [m for m in inner.split() if m]
                tokens.append({'type': 'group-bracket', 'moves': moves})
                i = j

            elif ch == ' ':
                i += 1

            else:
                # Bare move — collect the full move token
                j = i
                while j < len(alg) and alg[j] not in (' ', '(', ')', '[', ']'):
                    j += 1
                move = alg[i:j].strip()
                if move:
                    tokens.append({'type': 'move', 'moves': [move]})
                i = j

        # Render tokens to HTML
        parts = []
        for token in tokens:
            ttype = token['type']
            moves = token['moves']

            if ttype == 'group-paren':
                icons = ''.join(move_to_svg(m, 'group-paren') for m in moves)
                parts.append(
                    f'<span class="move-group move-group--paren">'
                    f'<span class="move-bracket">(</span>'
                    f'{icons}'
                    f'<span class="move-bracket">)</span>'
                    f'</span>'
                )

            elif ttype == 'group-bracket':
                icons = ''.join(move_to_svg(m, 'group-bracket') for m in moves)
                parts.append(
                    f'<span class="move-group move-group--bracket">'
                    f'<span class="move-bracket">[</span>'
                    f'{icons}'
                    f'<span class="move-bracket">]</span>'
                    f'</span>'
                )

            else:
                # Bare move — no wrapper span
                parts.append(move_to_svg(moves[0]))

        return mark_safe('\n'.join(parts))
    
    
    def get_top_layer_colors(self):
        """
        Generate color mapping for top layer SVG visualization.
        
        Imports patterns from separate OLL and PLL files for maintainability.
        Returns a dict with color values for each sticker position.
        
        For OLL: Yellow = oriented, Gray = not oriented
        For PLL: All yellow on top, side colors show permutation
        """
        from .oll_patterns import get_oll_pattern
        from .pll_patterns import get_pll_pattern
        
        # Try to get pattern from appropriate file
        pattern = None
        if self.slug.startswith('oll-'):
            pattern = get_oll_pattern(self.slug)
        elif self.slug.startswith('pll-'):
            pattern = get_pll_pattern(self.slug)
        
        # Default pattern if not found (solved cube)
        if not pattern:
            pattern = {
                'U': [
                    ['#FFD700', '#FFD700', '#FFD700'],
                    ['#FFD700', '#FFD700', '#FFD700'],
                    ['#FFD700', '#FFD700', '#FFD700'],
                ],
                'F': ['#00D800', '#00D800', '#00D800'],
                'R': ['#C41E3A', '#C41E3A', '#C41E3A'],
                'B': ['#0051BA', '#0051BA', '#0051BA'],
                'L': ['#FF5800', '#FF5800', '#FF5800'],
            }
        
        # Convert pattern to template format
        # Template expects: colors.U.0.0, colors.U.0.1, etc.
        colors = {
            'U': {
                '0': {
                    '0': pattern['U'][0][0],
                    '1': pattern['U'][0][1],
                    '2': pattern['U'][0][2],
                },
                '1': {
                    '0': pattern['U'][1][0],
                    '1': pattern['U'][1][1],
                    '2': pattern['U'][1][2],
                },
                '2': {
                    '0': pattern['U'][2][0],
                    '1': pattern['U'][2][1],
                    '2': pattern['U'][2][2],
                },
            },
            'F': {
                '0': {
                    '0': pattern.get('F', ['#00D800', '#00D800', '#00D800'])[0],
                    '1': pattern.get('F', ['#00D800', '#00D800', '#00D800'])[1],
                    '2': pattern.get('F', ['#00D800', '#00D800', '#00D800'])[2],
                }
            },
            'R': {
                '0': {
                    '0': pattern.get('R', ['#C41E3A', '#C41E3A', '#C41E3A'])[0],
                    '1': pattern.get('R', ['#C41E3A', '#C41E3A', '#C41E3A'])[1],
                    '2': pattern.get('R', ['#C41E3A', '#C41E3A', '#C41E3A'])[2],
                }
            },
            'B': {
                '0': {
                    '0': pattern.get('B', ['#0051BA', '#0051BA', '#0051BA'])[0],
                    '1': pattern.get('B', ['#0051BA', '#0051BA', '#0051BA'])[1],
                    '2': pattern.get('B', ['#0051BA', '#0051BA', '#0051BA'])[2],
                }
            },
            'L': {
                '0': {
                    # Note: L face is reversed (right to left in the pattern)
                    '0': pattern.get('L', ['#FF5800', '#FF5800', '#FF5800'])[2],
                    '1': pattern.get('L', ['#FF5800', '#FF5800', '#FF5800'])[1],
                    '2': pattern.get('L', ['#FF5800', '#FF5800', '#FF5800'])[0],
                }
            },
        }
        
        return colors



    def get_roofpig_config(self):
        """Generate Roofpig configuration string"""
        config_parts = []
        
        # Add algorithm
        if self.algorithm:
            config_parts.append(f"alg={self.algorithm}")
        
        # Add setup
        if self.roofpig_setup:
            config_parts.append(f"setup={self.roofpig_setup}")
        
        # Add colored pieces
        if self.roofpig_colored:
            config_parts.append(f"colored={self.roofpig_colored}")
        
        # Add flags
        flags = self.roofpig_flags or 'showalg'
        config_parts.append(f"flags={flags}")
        
        # Add hover for better 3D interaction
        config_parts.append("hover=2")
        
        return " | ".join(config_parts)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name