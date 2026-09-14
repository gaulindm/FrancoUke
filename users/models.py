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

    # 🆕 Which teleprompter style to jump to from the song list —
    # avoids showing two separate teleprompter buttons/columns per song.
    TELEPROMPTER_STYLE_CHOICES = [
        ("inline",   "Chord symbols inline"),
        ("beginner", "Chord diagrams above lyrics"),
    ]

    # 🆕 Common (PDF + Teleprompter) display preferences
    FONT_STYLE_CHOICES = [
        ("sans-serif", "Sans-serif"),
        ("serif",      "Serif"),
        ("monospace",  "Monospace"),
    ]

    # 🆕 Teleprompter-only for now. PDF line spacing is already handled
    # per-song via SongFormatting (see formatting_views.py) — this field
    # is not wired into PDF rendering.
    LINE_SPACING_CHOICES = [
        ("compact", "Compact"),
        ("normal",  "Normal"),
        ("relaxed", "Relaxed"),
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
    # --- Common (PDF + Teleprompter): instrument & chord-diagram shape ---
    is_lefty = models.BooleanField(default=False)
    # --- PDF-only ---
    is_printing_alternate_chord = models.BooleanField(default=False)
    known_chords = models.JSONField(default=list, blank=True)
    use_known_chord_filter = models.BooleanField(default=False)

    # --- Common (PDF + Teleprompter) display preferences ---
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
    font_size = models.IntegerField(default=18)
    font_style = models.CharField(
        max_length=20,
        choices=FONT_STYLE_CHOICES,
        default="sans-serif",
    )

    # --- Teleprompter-only ---
    teleprompter_style = models.CharField(
        max_length=10,
        choices=TELEPROMPTER_STYLE_CHOICES,
        default="inline",
    )
    theme = models.CharField(
        max_length=10,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
    )
    auto_scroll = models.BooleanField(default=False)
    scroll_speed = models.IntegerField(default=20)
    line_spacing = models.CharField(
        max_length=10,
        choices=LINE_SPACING_CHOICES,
        default="normal",
    )

    def __str__(self):
        sec = f", Secondary: {self.secondary_instrument}" if self.secondary_instrument else ""
        return f"{self.user.username} - {self.primary_instrument}{sec}"