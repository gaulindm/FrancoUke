# cubing_users/views.py
def cuber_login(request):
    """Login pour cubeurs (color code)"""
    if request.method == 'POST':
        color = request.POST.get('color')
        adjective = request.POST.get('adjective')
        superhero = request.POST.get('superhero')
        color_code = request.POST.get('color_code')
        
        # Vérifie identité + color code
        cuber = authenticate_cuber(color, adjective, superhero, color_code)
        if cuber:
            request.session['cuber_id'] = str(cuber.cuber_id)
            return redirect('cube:dashboard')
    
    return render(request, 'cubing_users/login.html')

# accounts/views.py (ou ukulele/views.py)
def ukulele_login(request):
    """Login traditionnel pour songbook"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # Django standard login
            return redirect('ukulele:songbook')
    
    return render(request, 'accounts/login.html')