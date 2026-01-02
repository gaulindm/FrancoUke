# cubing_users/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def cuber_required(view_func):
    """
    Décorateur qui vérifie qu'un cubeur est connecté.
    Redirige vers la page de login cubeur sinon.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request, 'cuber') or request.cuber is None:
            messages.warning(request, "Tu dois te connecter pour accéder à cette page.")
            return redirect('cubing_users:cuber_login')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def leader_required(view_func):
    """
    Décorateur qui vérifie qu'un leader est connecté.
    Redirige vers la page de login leader sinon.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez vous connecter en tant que leader.")
            return redirect('cubing_users:leader_login')
        
        if not hasattr(request.user, 'leader_profile'):
            messages.error(request, "Vous devez créer un profil de leader.")
            return redirect('cubing_users:leader_register')
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def cuber_or_leader_required(view_func):
    """
    Décorateur qui accepte soit un cubeur soit un leader.
    Utile pour les vues accessibles aux deux types d'utilisateurs.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        is_cuber = hasattr(request, 'cuber') and request.cuber is not None
        is_leader = request.user.is_authenticated and hasattr(request.user, 'leader_profile')
        
        if not (is_cuber or is_leader):
            messages.warning(request, "Tu dois te connecter pour accéder à cette page.")
            return redirect('cubing_users:cuber_login')
        
        return view_func(request, *args, **kwargs)
    return wrapped_view