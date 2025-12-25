from django.db import models
from django.utils.text import slugify
import json  # ← Add this line
from django.utils.safestring import mark_safe  # ← Add this line



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
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
