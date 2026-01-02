# cubing_users/middleware.py
from .models import Cuber

class CuberSessionMiddleware:
    """
    Middleware qui ajoute l'objet Cuber à la requête si un cubeur est connecté.
    Utilise la session Django pour maintenir l'état de connexion.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifie si un cubeur est connecté via la session
        cuber_id = request.session.get('cuber_id')
        
        if cuber_id:
            try:
                request.cuber = Cuber.objects.get(cuber_id=cuber_id)
            except Cuber.DoesNotExist:
                request.cuber = None
                # Nettoie la session si le cubeur n'existe plus
                if 'cuber_id' in request.session:
                    del request.session['cuber_id']
        else:
            request.cuber = None
        
        response = self.get_response(request)
        return response