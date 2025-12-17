from django.db import models
from django.utils.text import slugify


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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
