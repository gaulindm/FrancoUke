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