# users/models.py - APRÈS (correct)
import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractUser  # ← Vérifie que c'est là!


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username


# ✅ Utilise settings.AUTH_USER_MODEL au lieu de User
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        UserPreference.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_preference(sender, instance, **kwargs):
    if hasattr(instance, 'userpreference'):
        instance.userpreference.save()



class UserPreference(models.Model):

    BRACKET_CHOICES = [
        ("square",      "Square brackets [Am]"),
        ("parentheses", "Parentheses (Am)"),
        ("curly",       "Curly braces {Am}"),
    ]

    CHORD_COLOR_CHOICES = [
        ("black", "Black"),
        ("red",   "Red"),
        ("blue",  "Blue"),
        ("green", "Green"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='userpreference'
    )
    transpose_value = models.IntegerField(default=0)
    primary_instrument = models.CharField(
        max_length=20,
        choices=[
            ("guitar",          "Guitar"),
            ("guitalele",       "Guitalele"),
            ("ukulele",         "Ukulele"),
            ("baritone_ukulele","Baritone Ukulele"),
            ("banjo",           "Banjo"),
            ("mandolin",        "Mandolin"),
        ],
        default="ukulele"
    )
    secondary_instrument = models.CharField(
        max_length=20,
        choices=[
            ("guitar",          "Guitar"),
            ("guitalele",       "Guitalele"),
            ("ukulele",         "Ukulele"),
            ("baritone_ukulele","Baritone Ukulele"),
            ("banjo",           "Banjo"),
            ("mandolin",        "Mandolin"),
        ],
        null=True,
        blank=True
    )
    is_lefty = models.BooleanField(default=False)
    is_printing_alternate_chord = models.BooleanField(default=False)
    known_chords = models.JSONField(default=list, blank=True)
    use_known_chord_filter = models.BooleanField(default=False)

    # --- Chord display preferences ---
    chord_bracket_style = models.CharField(
        max_length=20,
        choices=BRACKET_CHOICES,
        default="square",
    )
    chord_color = models.CharField(
        max_length=10,
        choices=CHORD_COLOR_CHOICES,
        default="red",
    )

    def __str__(self):
        sec = f", Secondary: {self.secondary_instrument}" if self.secondary_instrument else ""
        return f"{self.user.username} - {self.primary_instrument}{sec}"