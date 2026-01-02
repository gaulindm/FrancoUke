# cubing_users/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone  # ← Ajoute cet import

class Cuber(models.Model):
    """Utilisateur cubeur anonyme (enfants)"""
    cuber_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    color = models.CharField(max_length=10)
    adjective = models.CharField(max_length=50)
    superhero = models.CharField(max_length=50)
    color_code_hash = models.CharField(max_length=128)
    avatar_variant = models.CharField(max_length=20, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_active_date = models.DateTimeField(auto_now=True)
    
    # ✅ Lien OPTIONNEL vers compte traditionnel
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # users.CustomUser
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuber_profiles'
    )
    
    def __str__(self):
        return f"{self.color} {self.adjective} {self.superhero}"


class Leader(models.Model):
    """Leader (prof/coach) - utilise auth traditionnelle"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leader_profile'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('teacher', 'Enseignant'),
            ('coach', 'Entraîneur'),
            ('club_leader', 'Animateur de Club'),
            ('parent', 'Parent Responsable'),
        ]
    )
    organization = models.CharField(max_length=200, blank=True)
    
    # ✅ Juste auto_now_add, pas de default
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

class Group(models.Model):
    """Classe ou club de cubing"""
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    group_name = models.CharField(max_length=200)
    group_code = models.CharField(max_length=6, unique=True)
    group_type = models.CharField(
        max_length=20,
        choices=[
            ('class', 'Classe'),
            ('club', 'Club'),
            ('team', 'Équipe'),
            ('practice', 'Groupe de Pratique'),
        ]
    )
    # Leaders peuvent être multiples
    leaders = models.ManyToManyField(Leader, related_name='groups')
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.group_name


class GroupMembership(models.Model):
    """Relation N-to-N Cuber ↔ Group"""
    cuber = models.ForeignKey(Cuber, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Actif'),
            ('inactive', 'Inactif'),
        ],
        default='active'
    )
    
    class Meta:
        unique_together = ('cuber', 'group')
    
    def __str__(self):
        return f"{self.cuber} → {self.group.group_name}"