# cubing_users/authentication.py
from django.contrib.auth.hashers import check_password, make_password
from .models import Cuber

class CuberAuthenticationBackend:
    """
    Backend d'authentification custom pour les cubeurs.
    Authentifie avec: color + adjective + superhero + color_code
    """
    
    def authenticate(self, request, color=None, adjective=None, superhero=None, color_code=None, **kwargs):
        """
        Authentifie un cubeur avec son identité et son code couleur.
        
        Args:
            color: Rouge, Bleu, Vert, Jaune, Orange, Blanc
            adjective: Rapide, Éclair, Génial, etc.
            superhero: Solveur, Maître, Cubeur, etc.
            color_code: Liste de 6 couleurs (ex: ['Rouge', 'Bleu', 'Vert', 'Jaune', 'Orange', 'Blanc'])
        
        Returns:
            Cuber object si authentification réussie, None sinon
        """
        if not all([color, adjective, superhero, color_code]):
            return None
        
        try:
            # Trouve le cubeur par son identité
            cuber = Cuber.objects.get(
                color=color,
                adjective=adjective,
                superhero=superhero
            )
            
            # Vérifie le color_code
            if check_password(color_code, cuber.color_code_hash):
                return cuber
            
        except Cuber.DoesNotExist:
            # Crée un hash dummy pour éviter le timing attack
            make_password(color_code)
        
        return None
    
    def get_user(self, cuber_id):
        """
        Récupère un cubeur par son ID.
        Utilisé par Django pour maintenir la session.
        """
        try:
            return Cuber.objects.get(pk=cuber_id)
        except Cuber.DoesNotExist:
            return None


# Fonctions helper pour gérer les color codes
def hash_color_code(color_code):
    """
    Hash un color_code (liste de 6 couleurs) de façon sécurisée.
    
    Args:
        color_code: Liste ou string (ex: ['Rouge', 'Bleu', ...] ou "Rouge,Bleu,...")
    
    Returns:
        String hashé
    """
    if isinstance(color_code, list):
        color_code = ','.join(color_code)
    return make_password(color_code)


def verify_color_code(color_code, hashed):
    """
    Vérifie si un color_code correspond au hash.
    
    Args:
        color_code: Liste ou string
        hashed: Le hash stocké en DB
    
    Returns:
        Boolean
    """
    if isinstance(color_code, list):
        color_code = ','.join(color_code)
    return check_password(color_code, hashed)


def generate_color_code():
    """
    Génère un color_code aléatoire de 6 couleurs.
    
    Returns:
        Liste de 6 couleurs
    """
    import random
    colors = ['Rouge', 'Bleu', 'Vert', 'Jaune', 'Orange', 'Blanc']
    return [random.choice(colors) for _ in range(6)]


def is_color_code_unique(color, adjective, superhero, color_code):
    """
    Vérifie si cette combinaison identité + color_code est unique.
    
    Returns:
        Boolean
    """
    try:
        cuber = Cuber.objects.get(
            color=color,
            adjective=adjective,
            superhero=superhero
        )
        # L'identité existe, vérifie si le color_code est différent
        return not verify_color_code(color_code, cuber.color_code_hash)
    except Cuber.DoesNotExist:
        # L'identité n'existe pas, donc c'est unique
        return True