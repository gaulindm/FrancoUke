"""
Home page and legacy views for Francontcube.

Contains:
- Main home/landing page
- Method overview pages (coming soon)
- Legacy views for backward compatibility
"""

from django.shortcuts import render, get_object_or_404
from cube.models import CubeState


def home(request):
    """
    Main landing page for Francontcube.
    
    Displays a menu of available methods and features.
    """
    menu = [
        {
            'name': 'Training Hub',
            'desc': 'Practice finger tricks and algorithms to improve your speed',
            'icon': 'bi-stopwatch',
            'logo': None,
            'url': '/francontcube/training/',
            'available': False,
        },
        {
            'name': 'Méthode Apprenti Cubi',
            'desc': 'Apprenez à résoudre le cube 3×3 avec la méthode couche par couche',
            'icon': 'bi-book',
            'logo': None,
            'url': '/francontcube/methods/cubienewbie/',
            'available': True,
        },
        {
            'name': 'Méthode Débutant',
            'desc': 'Apprenez des nouvelles algo pour résoudre le cube 3×3 avec la méthode couche par couche',
            'icon': 'bi-book',
            'logo': None,
            'url': '/francontcube/methods/beginner/',
            'available': True,
        },
        {
            'name': 'CFOP',
            'desc': 'Méthode avancée : Cross, F2L, OLL, PLL',
            'icon': 'bi-lightning',
            'logo': None,
            'url': '/francontcube/methods/cfop/',
            'available': True,
        },
        {
            'name': 'Algorithmes',
            'desc': 'Collection complète d\'algorithmes OLL et PLL',
            'icon': 'bi-grid-3x3',
            'logo': None,
            'url': '/francontcube/algorithms/',
            'available': False,
        },
        {
            'name': 'Timer',
            'desc': 'Chronomètre pour mesurer vos temps de résolution',
            'icon': 'bi-clock',
            'logo': None,
            'url': '/francontcube/timer/',
            'available': False,
        },
        {
            'name': 'Ressources',
            'desc': 'Liens utiles, vidéos et guides supplémentaires',
            'icon': 'bi-collection',
            'logo': None,
            'url': '/francontcube/resources/',
            'available': False,
        },
    ]
    
    return render(request, 'francontcube/home.html', {'menu': menu})


# ============================================================
# OTHER METHODS (Coming Soon)
# ============================================================

def method_beginner(request):
    """
    Beginner method page (CFOP intro).
    
    TODO: Implement full CFOP method when ready.
    """
    return render(request, 'francontcube/methods/beginner/index.html')


def method_f2l(request):
    """
    F2L method page.
    
    TODO: Implement F2L specific content.
    """
    return render(request, 'francontcube/methods/f2l/index.html')


def method_roux(request):
    """
    Roux method page.
    
    TODO: Implement Roux method when ready.
    """
    return render(request, 'francontcube/methods/roux/index.html')


# ============================================================
# LEGACY VIEWS
# ============================================================
# These views are kept for backward compatibility.
# Consider removing or updating these when refactoring is complete.

def slides(request):
    """Legacy slides view."""
    return render(request, "francontcube/slides.html")


def pdfs(request):
    """Legacy PDFs view."""
    return render(request, "francontcube/pdfs.html")


def videos(request):
    """Legacy videos view."""
    return render(request, "francontcube/videos.html")


def ressources3par3(request):
    """Legacy 3x3 resources view."""
    return render(request, "francontcube/ressources3par3.html")


def tutorial_step(request, slug):
    """
    Dynamic step loader - legacy view.
    
    This is probably not needed anymore with the new view structure.
    Consider deprecating once all steps are migrated to the new system.
    
    Args:
        request: Django HttpRequest
        slug: Slug of the CubeState to display
        
    Returns:
        HttpResponse with rendered step template
    """
    cube_state = get_object_or_404(CubeState, slug=slug)
    return render(request, "francontcube/methods/step.html", {
        "json_state": cube_state.json_state,
        "cube": cube_state
    })