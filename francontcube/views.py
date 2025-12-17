from django.shortcuts import render, get_object_or_404
from cube.models import CubeState


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def build_breadcrumbs(method_name=None, step_name=None, step_icon=None):
    """
    Helper function to build breadcrumbs consistently.
    
    Args:
        method_name: Name of the method (e.g., "Apprenti Cubi")
        step_name: Name of the step (e.g., "Croix Blanche")
        step_icon: Bootstrap icon for the step (e.g., "plus-circle")
    
    Returns:
        List of breadcrumb dictionaries
    """
    breadcrumbs = []
    
    if method_name:
        breadcrumbs.append({
            'name': 'Méthodes',
            'url': '/francontcube/',
            'icon': 'book'
        })
        
        method_urls = {
            'Apprenti Cubi': '/francontcube/methods/cubienewbie/',
            'CFOP': '/francontcube/methods/beginner/',
            'F2L': '/francontcube/methods/f2l/',
            'Roux': '/francontcube/methods/roux/',
        }
        
        breadcrumbs.append({
            'name': method_name,
            'url': method_urls.get(method_name, ''),
            'icon': 'star-fill'
        })
    
    if step_name:
        breadcrumbs.append({
            'name': step_name,
            'url': '',  # Current page, no URL
            'icon': step_icon or 'circle'
        })
    
    return breadcrumbs


# ============================================================
# HOME PAGE
# ============================================================
def home(request):
    menu = [
        {
            'name': 'Training Hub',
            'desc': 'Practice finger tricks and algorithms to improve your speed',
            'icon': 'bi-stopwatch',
            'logo': None,
            'url': '/francontcube/training/',
            "available": False,
        },
        {
            'name': 'Méthode Apprenti Cubi',
            'desc': 'Apprenez à résoudre le cube 3×3 avec la méthode couche par couche',
            'icon': 'bi-book',
            'logo': None,
            'url': '/francontcube/methods/cubienewbie/',
            "available": True,
        },
        {
            'name': 'CFOP',
            'desc': 'Méthode avancée : Cross, F2L, OLL, PLL',
            'icon': 'bi-lightning',
            'logo': None,
            'url': '/francontcube/methods/beginner/',
            "available": False,
        },
        {
            'name': 'Algorithmes',
            'desc': 'Collection complète d\'algorithmes OLL et PLL',
            'icon': 'bi-grid-3x3',
            'logo': None,
            'url': '/francontcube/algorithms/',
            "available": False,
        },
        {
            'name': 'Timer',
            'desc': 'Chronomètre pour mesurer vos temps de résolution',
            'icon': 'bi-clock',
            'logo': None,
            'url': '/francontcube/timer/',
            "available": False,
        },
        {
            'name': 'Ressources',
            'desc': 'Liens utiles, vidéos et guides supplémentaires',
            'icon': 'bi-collection',
            'logo': None,
            'url': '/francontcube/resources/',
            "available": False,
        },
    ]
    
    return render(request, 'francontcube/home.html', {'menu': menu})


# ============================================================
# CUBIE NEWBIE METHOD - MAIN PAGE
# ============================================================
def method_cubienewbie(request):
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '', 'icon': 'star-fill'},
    ]
    
    steps = [
        {
            "name": "1 — Le cube",
            "desc": "Comprendre les pièces, la structure et le fonctionnement.",
            "icon": "bi-cube",
            "url": "/francontcube/methods/cubienewbie/cube/",
            "available": False,
        },
        {
            "name": "2 — La notation",
            "desc": "Apprendre comment lire les mouvements (R, L, U, F…).",
            "icon": "bi-pencil",
            "url": "/francontcube/methods/cubienewbie/notation/",
            "available": True,
        },
        {
            "name": "3 — Étape 1a : La marguerite",
            "desc": "Premier objectif : construire la marguerite autour du centre jaune.",
            "icon": "bi-flower3",
            "url": "/francontcube/methods/cubienewbie/daisy/",
            "available": True,
        },
        {
            "name": "4 — Étape 1b : La croix blanche",
            "desc": "Aligner les arêtes blanches avec les centres pour former la croix.",
            "icon": "bi-plus-circle",
            "url": "/francontcube/methods/cubienewbie/white-cross/",
            "available": True,
        },
        {
            "name": "5 — Étape 2 : Les coins inférieurs",
            "desc": "Placer les coins inferieurs blancs pour compléter la première couche.",
            "icon": "bi-box",
            "url": "/francontcube/methods/cubienewbie/bottom-corners/",
            "available": True,
        },
        {
            "name": "6 — Étape 3 : Les bords du milieu",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": "/francontcube/methods/cubienewbie/second-layer/",
            "available": True,
        },
        {
            "name": "7 — Étape 4 : La croix jaune",
            "desc": "Former la croix jaune sur la face supérieure.",
            "icon": "bi-plus-circle",
            "url": "/francontcube/methods/cubienewbie/yellow-cross/",
            "available": True,
        },
        {
            "name": "8 — Étape 5 : La face jaune",
            "desc": "La chasse au poisson.",
            "icon": "bi-brightness-high",
            "url": "/francontcube/methods/cubienewbie/yellow-face/",
            "available": True,
        },
        {
            "name": "9 — Étape 6 : La permutation des coins jaunes",
            "desc": "Placer les coins à leur bon emplacement.",
            "icon": "bi-arrow-repeat",
            "url": "/francontcube/methods/cubienewbie/corner-permutation/",
            "available": True,
        },
        {
            "name": "10 — Étape 7 : La permutation des arêtes",    
            "desc": "La permutation des arêtes de la couche jaune pour finir le cube.",
            "icon": "bi-check-circle",
            "url": "/francontcube/methods/cubienewbie/edge-permutation/",
            "available": True,
        },
    ]

    return render(request, "francontcube/methods/cubienewbie/index.html", {
        "steps": steps,
        "breadcrumbs": breadcrumbs
    })


# ============================================================
# CUBIE NEWBIE METHOD - INDIVIDUAL STEPS
# ============================================================
def notation(request):
    """Beginner method page (CFOP intro)"""
    return render(request, 'francontcube/methods/cubienewbie/notation.html')


def daisy(request):
    """Step 1a: Build the daisy around yellow center"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'La Marguerite', 'url': '', 'icon': 'flower3'},
    ]
    
    goal = get_object_or_404(CubeState, slug="marguerite-goal")
    before = get_object_or_404(CubeState, slug="marguerite-before")
    after = get_object_or_404(CubeState, slug="marguerite-after")

    return render(request, "francontcube/methods/cubienewbie/daisy.html", {
        "goal_state": goal.json_state,
        "before_state": before.json_state,
        "after_state": after.json_state,
        "breadcrumbs": breadcrumbs,
    })



def white_cross(request):
    """Step 1b: White cross on bottom"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Croix Blanche', 'url': '', 'icon': 'plus-circle'},
    ]
    
    # Helper function to safely get cube state
    def get_cube_state_safe(slug):
        try:
            return CubeState.objects.get(slug=slug)
        except CubeState.DoesNotExist:
            return None
    
    # Load all cube states needed for this page
    goal = get_cube_state_safe("white-cross-goal")
    before = get_cube_state_safe("white-cross-before")
    after = get_cube_state_safe("white-cross-after")
    
    # Progression states (0-4 edges placed)
    progress_0 = get_cube_state_safe("white-cross-progress-0")
    progress_1 = get_cube_state_safe("white-cross-progress-1")
    progress_2 = get_cube_state_safe("white-cross-progress-2")
    progress_3 = get_cube_state_safe("white-cross-progress-3")
    progress_4 = get_cube_state_safe("white-cross-progress-4")
    
    # Comparison states
    wrong = get_cube_state_safe("white-cross-wrong")
    correct = get_cube_state_safe("white-cross-correct")
    
    # Collect missing slugs for helpful error messages
    missing_slugs = []
    state_map = {
        'white-cross-goal': goal,
        'white-cross-before': before,
        'white-cross-after': after,
        'white-cross-progress-0': progress_0,
        'white-cross-progress-1': progress_1,
        'white-cross-progress-2': progress_2,
        'white-cross-progress-3': progress_3,
        'white-cross-progress-4': progress_4,
        'white-cross-wrong': wrong,
        'white-cross-correct': correct,
    }
    
    for slug, state in state_map.items():
        if state is None:
            missing_slugs.append(slug)
    
    return render(request, 'francontcube/methods/cubienewbie/white-cross.html', {
        'breadcrumbs': breadcrumbs,
        'goal_state': goal.json_state if goal else None,
        'before_state': before.json_state if before else None,
        'after_state': after.json_state if after else None,
        'progress_states': [
            progress_0.json_state if progress_0 else None,
            progress_1.json_state if progress_1 else None,
            progress_2.json_state if progress_2 else None,
            progress_3.json_state if progress_3 else None,
            progress_4.json_state if progress_4 else None,
        ],
        'wrong_state': wrong.json_state if wrong else None,
        'correct_state': correct.json_state if correct else None,
        'missing_slugs': missing_slugs,
    })


def bottom_corners(request):
    """Step 2: Bottom white corners"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Coins Inférieurs', 'url': '', 'icon': 'box'},
    ]
    
    # Helper function to safely get cube state
    def get_cube_state_safe(slug):
        try:
            return CubeState.objects.get(slug=slug)
        except CubeState.DoesNotExist:
            return None
    
    # Load all cube states needed for this page
    before = get_cube_state_safe("bottom-corners-before")
    goal = get_cube_state_safe("bottom-corners-goal")
    
    # The 3 algorithm cases
    case_1 = get_cube_state_safe("bottom-corners-case-1")  # white on right
    case_2 = get_cube_state_safe("bottom-corners-case-2")  # white on front
    case_3 = get_cube_state_safe("bottom-corners-case-3")  # white on top
    
    # Collect missing slugs for helpful error messages
    missing_slugs = []
    state_map = {
        'bottom-corners-before': before,
        'bottom-corners-goal': goal,
        'bottom-corners-case-1': case_1,
        'bottom-corners-case-2': case_2,
        'bottom-corners-case-3': case_3,
    }
    
    for slug, state in state_map.items():
        if state is None:
            missing_slugs.append(slug)
    
    return render(request, 'francontcube/methods/cubienewbie/bottom-corners.html', {
        'breadcrumbs': breadcrumbs,
        'before_state': before.json_state if before else None,
        'goal_state': goal.json_state if goal else None,
        'case_1_state': case_1.json_state if case_1 else None,
        'case_2_state': case_2.json_state if case_2 else None,
        'case_3_state': case_3.json_state if case_3 else None,
        'missing_slugs': missing_slugs,
    })

def second_layer(request):
    """Step 3: Middle layer edges"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Deuxième Couche', 'url': '', 'icon': 'arrows-expand'},
    ]
    
    # Helper function to safely get cube state
    def get_cube_state_safe(slug):
        try:
            return CubeState.objects.get(slug=slug)
        except CubeState.DoesNotExist:
            return None
    
    # Load all cube states needed for this page
    before = get_cube_state_safe("second-layer-before")
    goal = get_cube_state_safe("second-layer-goal")
    
    # Algorithm cases
    case_back = get_cube_state_safe("second-layer-case-back")
    case_front = get_cube_state_safe("second-layer-case-front")
    
    # Special cases
    edge_yellow = get_cube_state_safe("second-layer-edge-yellow")
    edge_stuck = get_cube_state_safe("second-layer-edge-stuck")
    
    # Collect missing slugs for helpful error messages
    missing_slugs = []
    state_map = {
        'second-layer-before': before,
        'second-layer-goal': goal,
        'second-layer-case-back': case_back,
        'second-layer-case-front': case_front,
        'second-layer-edge-yellow': edge_yellow,
        'second-layer-edge-stuck': edge_stuck,
    }
    
    for slug, state in state_map.items():
        if state is None:
            missing_slugs.append(slug)
    
    return render(request, 'francontcube/methods/cubienewbie/second-layer.html', {
        'breadcrumbs': breadcrumbs,
        'before_state': before.json_state if before else None,
        'goal_state': goal.json_state if goal else None,
        'case_back_state': case_back.json_state if case_back else None,
        'case_front_state': case_front.json_state if case_front else None,
        'edge_yellow_state': edge_yellow.json_state if edge_yellow else None,
        'edge_stuck_state': edge_stuck.json_state if edge_stuck else None,
        'missing_slugs': missing_slugs,
    })






def yellow_cross(request):
    """Step 4: Yellow cross on top"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Croix Jaune', 'url': '', 'icon': 'plus-circle'},
    ]
    return render(request, 'francontcube/methods/cubienewbie/yellow-cross.html', {'breadcrumbs': breadcrumbs})


def yellow_face(request):
    """Step 5: Complete yellow face (fish hunt)"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Face Jaune', 'url': '', 'icon': 'brightness-high'},
    ]
    return render(request, 'francontcube/methods/cubienewbie/yellow-face.html', {'breadcrumbs': breadcrumbs})


def corner_permutation(request):
    """Step 6: Permute yellow corners"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Permutation Coins', 'url': '', 'icon': 'arrow-repeat'},
    ]
    return render(request, 'francontcube/methods/cubienewbie/corner-permutation.html', {'breadcrumbs': breadcrumbs})


def edge_permutation(request):
    """Step 7: Permute yellow edges (final step)"""
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Apprenti Cubi', 'url': '/francontcube/methods/cubienewbie/', 'icon': 'star-fill'},
        {'name': 'Permutation Arêtes', 'url': '', 'icon': 'check-circle'},
    ]
    return render(request, 'francontcube/methods/cubienewbie/edge-permutation.html', {'breadcrumbs': breadcrumbs})





# ============================================================
# OTHER METHODS (Coming Soon)
# ============================================================
def method_beginner(request):
    """Beginner method page (CFOP intro)"""
    return render(request, 'francontcube/methods/beginner/index.html')


def method_f2l(request):
    """F2L method page"""
    return render(request, 'francontcube/methods/f2l/index.html')


def method_roux(request):
    """Roux method page"""
    return render(request, 'francontcube/methods/roux/index.html')


# ============================================================
# LEGACY / UNUSED (Keep for reference, can be deleted later)
# ============================================================
def slides(request):
    return render(request, "francontcube/slides.html")

def pdfs(request):
    return render(request, "francontcube/pdfs.html")

def videos(request):
    return render(request, "francontcube/videos.html")

def ressources3par3(request):
    return render(request, "francontcube/ressources3par3.html")

def tutorial_step(request, slug):
    """Dynamic step loader - probably not needed anymore"""
    cube_state = get_object_or_404(CubeState, slug=slug)
    return render(request, "francontcube/methods/step.html", {
        "json_state": cube_state.json_state,
        "cube": cube_state
    })