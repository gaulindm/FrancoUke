# training/utils.py

def get_user_type(request):
    """
    Détermine le type d'utilisateur (Leader ou Cuber)
    
    Returns:
        dict: {
            'is_leader': bool,
            'is_cuber': bool,
            'leader': Leader object or None,
            'cuber': Cuber object or None
        }
    """
    from cubing_users.models import Leader, Cuber
    
    result = {
        'is_leader': False,
        'is_cuber': False,
        'leader': None,
        'cuber': None
    }
    
    # Vérifier Leader
    if request.user.is_authenticated:
        try:
            leader = Leader.objects.get(user=request.user)
            result['is_leader'] = True
            result['leader'] = leader
        except Leader.DoesNotExist:
            pass
    
    # Vérifier Cuber
    cuber_id = request.session.get('cuber_id')
    if cuber_id:
        try:
            cuber = Cuber.objects.get(cuber_id=cuber_id)
            result['is_cuber'] = True
            result['cuber'] = cuber
        except Cuber.DoesNotExist:
            pass
    
    return result