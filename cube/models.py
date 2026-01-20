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
        """Generate SVG icons from algorithm string"""
        if not self.algorithm or self.algorithm.strip() == '':
            return ''
        
        moves = self.algorithm.strip().split()
        svg_list = []
        
        for move in moves:
            svg_id = move.replace("'", "-prime").replace("2", "2")
            svg_list.append(f'<svg class="move-icon"><use href="#{svg_id}"/></svg>')
        
        return mark_safe('\n                            '.join(svg_list))
    
    
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