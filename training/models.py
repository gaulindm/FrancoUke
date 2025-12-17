# training/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Min, Avg, Count

class Algorithm(models.Model):
    """Différents algorithmes que les élèves peuvent pratiquer"""
    
    DIFFICULTY_CHOICES = [
        ('apprenti', 'Apprenti Cubi'),
        ('confirme', 'Cubiste Confirmé'),
        ('speedcube', 'Speedcubiste'),
        ('maitre', 'Maître Cubi'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    notation = models.CharField(max_length=200)  # e.g., "R U R' U'"
    repetitions = models.IntegerField(default=6, verbose_name="Répétitions")
    difficulty = models.CharField(
        max_length=20, 
        choices=DIFFICULTY_CHOICES,
        verbose_name="Niveau"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, blank=True, verbose_name="Catégorie")
    
    def __str__(self):
        return f"{self.name} ({self.notation})"
    
    class Meta:
        verbose_name = "Algorithme"
        verbose_name_plural = "Algorithmes"
        ordering = ['difficulty', 'name']

# training/models.py

class TrainingSession(models.Model):
    """Session de pratique individuelle"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    time_ms = models.IntegerField(verbose_name="Temps (ms)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'algorithm', '-created_at']),
        ]
        verbose_name = "Session d'entraînement"
        verbose_name_plural = "Sessions d'entraînement"
    
    def __str__(self):
        username = self.user.username if self.user else "Anonyme"
        return f"{username} - {self.algorithm.name} - {self.time_ms}ms"
    
    @property
    def time_formatted(self):
        """Retourne le temps en format MM:SS.MS"""
        if self.time_ms is None:
            return "-"
        
        total_seconds = self.time_ms // 1000
        milliseconds = (self.time_ms % 1000) // 10
        seconds = total_seconds % 60
        minutes = total_seconds // 60
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"


class UserProgress(models.Model):
    """Statistiques agrégées par utilisateur et algorithme"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    best_time_ms = models.IntegerField(verbose_name="Meilleur temps (ms)")
    total_attempts = models.IntegerField(default=0, verbose_name="Tentatives totales")
    last_practiced = models.DateTimeField(auto_now=True, verbose_name="Dernière pratique")
    
    class Meta:
        unique_together = ['user', 'algorithm']
        verbose_name = "Progrès utilisateur"
        verbose_name_plural = "Progrès utilisateurs"
    
    def __str__(self):
        return f"{self.user.username} - {self.algorithm.name} - Record: {self.best_time_ms}ms"
    
    @property
    def best_time_formatted(self):
        """Retourne le meilleur temps en format MM:SS.MS"""
        if self.best_time_ms is None:
            return "-"
        
        total_seconds = self.best_time_ms // 1000
        milliseconds = (self.best_time_ms % 1000) // 10
        seconds = total_seconds % 60
        minutes = total_seconds // 60
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
    
