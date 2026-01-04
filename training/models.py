# training/models.py
from django.db import models
from django.conf import settings
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


class TrainingSession(models.Model):
    """
    Session de pratique individuelle
    Supporte 3 types d'utilisateurs:
    - Cuber (enfant avec UUID)
    - Leader (adulte avec compte traditionnel)
    - Anonyme (visiteur sans compte)
    """
    # Relations optionnelles vers les différents types d'utilisateurs
    cuber = models.ForeignKey(
        'cubing_users.Cuber',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='training_sessions'
    )
    leader = models.ForeignKey(
        'cubing_users.Leader',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='training_sessions'
    )
    # Pour compatibilité avec sessions anonymes web (fallback)
    session_key = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Clé de session pour utilisateurs anonymes"
    )
    
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    time_ms = models.IntegerField(verbose_name="Temps (ms)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cuber', 'algorithm', '-created_at']),
            models.Index(fields=['leader', 'algorithm', '-created_at']),
            models.Index(fields=['session_key', 'algorithm', '-created_at']),
        ]
        verbose_name = "Session d'entraînement"
        verbose_name_plural = "Sessions d'entraînement"
    
    def __str__(self):
        if self.cuber:
            username = str(self.cuber)
        elif self.leader:
            username = str(self.leader.user.get_full_name() or self.leader.user.username)
        else:
            username = "Anonyme"
        return f"{username} - {self.algorithm.name} - {self.time_ms}ms"
    
    @property
    def user_display(self):
        """Retourne le nom d'affichage de l'utilisateur"""
        if self.cuber:
            return str(self.cuber)
        elif self.leader:
            return self.leader.user.get_full_name() or self.leader.user.username
        return "Anonyme"
    
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


class CuberProgress(models.Model):
    """Statistiques agrégées pour un Cuber (enfant)"""
    cuber = models.ForeignKey(
        'cubing_users.Cuber',
        on_delete=models.CASCADE,
        related_name='algorithm_progress'
    )
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    best_time_ms = models.IntegerField(verbose_name="Meilleur temps (ms)")
    total_attempts = models.IntegerField(default=0, verbose_name="Tentatives totales")
    last_practiced = models.DateTimeField(auto_now=True, verbose_name="Dernière pratique")
    
    class Meta:
        unique_together = ['cuber', 'algorithm']
        verbose_name = "Progrès Cuber"
        verbose_name_plural = "Progrès Cubers"
    
    def __str__(self):
        return f"{self.cuber} - {self.algorithm.name} - Record: {self.best_time_ms}ms"
    
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


class LeaderProgress(models.Model):
    """Statistiques agrégées pour un Leader (adulte)"""
    leader = models.ForeignKey(
        'cubing_users.Leader',
        on_delete=models.CASCADE,
        related_name='algorithm_progress'
    )
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    best_time_ms = models.IntegerField(verbose_name="Meilleur temps (ms)")
    total_attempts = models.IntegerField(default=0, verbose_name="Tentatives totales")
    last_practiced = models.DateTimeField(auto_now=True, verbose_name="Dernière pratique")
    
    class Meta:
        unique_together = ['leader', 'algorithm']
        verbose_name = "Progrès Leader"
        verbose_name_plural = "Progrès Leaders"
    
    def __str__(self):
        username = self.leader.user.get_full_name() or self.leader.user.username
        return f"{username} - {self.algorithm.name} - Record: {self.best_time_ms}ms"
    
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


# ========================================
# Helper Functions pour récupérer les progrès
# ========================================

def get_user_progress(request, algorithm):
    """
    Récupère les progrès de l'utilisateur actuel (Cuber ou Leader)
    Returns: (progress_object, is_cuber, is_leader)
    """
    # Vérifier si c'est un Cuber (depuis session)
    cuber_id = request.session.get('cuber_id')
    if cuber_id:
        try:
            from cubing_users.models import Cuber
            cuber = Cuber.objects.get(cuber_id=cuber_id)
            progress = CuberProgress.objects.filter(
                cuber=cuber,
                algorithm=algorithm
            ).first()
            return progress, True, False
        except:
            pass
    
    # Vérifier si c'est un Leader (authentification traditionnelle)
    if request.user.is_authenticated:
        try:
            from cubing_users.models import Leader
            leader = Leader.objects.get(user=request.user)
            progress = LeaderProgress.objects.filter(
                leader=leader,
                algorithm=algorithm
            ).first()
            return progress, False, True
        except Leader.DoesNotExist:
            pass
    
    return None, False, False


def get_recent_times(request, algorithm, limit=10):
    """
    Récupère les temps récents de l'utilisateur actuel
    """
    # Cuber
    cuber_id = request.session.get('cuber_id')
    if cuber_id:
        return TrainingSession.objects.filter(
            cuber_id=cuber_id,
            algorithm=algorithm
        ).order_by('-created_at')[:limit]
    
    # Leader
    if request.user.is_authenticated:
        try:
            from cubing_users.models import Leader
            leader = Leader.objects.get(user=request.user)
            return TrainingSession.objects.filter(
                leader=leader,
                algorithm=algorithm
            ).order_by('-created_at')[:limit]
        except:
            pass
    
    # Anonyme - utiliser session_key
    session_key = request.session.session_key
    if session_key:
        return TrainingSession.objects.filter(
            session_key=session_key,
            algorithm=algorithm
        ).order_by('-created_at')[:limit]
    
    return TrainingSession.objects.none()