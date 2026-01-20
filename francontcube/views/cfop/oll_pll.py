# francontcube/views/cfop/oll_pll.py

from django.shortcuts import render
from cube.models import CubeState

# ============================================================================
# OLL CATEGORIES (57 cases total)
# ============================================================================
OLL_CATEGORIES = {
    'oll-cross': {
        'name': 'Cross (Résolu)',
        'description': 'Tous les stickers du dessus sont jaunes - Aucun algorithme nécessaire',
        'slug_prefix': 'oll-01',
        'icon': 'bi-check-circle-fill',
        'color': 'success',
        'count': 1
    },
    'oll-dot': {
        'name': 'Dot (Point)',
        'description': 'Seulement le centre est jaune - 8 cas incluant Sune et Anti-Sune',
        'slug_prefix': 'oll-',
        'icon': 'bi-circle-fill',
        'color': 'warning',
        'count': 8
    },
    'oll-line': {
        'name': 'Line (Ligne)',
        'description': 'Une ligne horizontale jaune - 8 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-dash-lg',
        'color': 'info',
        'count': 8
    },
    'oll-l-shape': {
        'name': 'L-Shape (Forme L)',
        'description': 'Forme en L dans le coin - 6 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-arrow-return-right',
        'color': 'primary',
        'count': 6
    },
    'oll-square': {
        'name': 'Square (Carré)',
        'description': 'Carré jaune dans le coin - 4 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-square-fill',
        'color': 'danger',
        'count': 4
    },
    'oll-lightning': {
        'name': 'Lightning (Éclair)',
        'description': 'Forme d\'éclair - 8 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-lightning-fill',
        'color': 'warning',
        'count': 8
    },
    'oll-fish': {
        'name': 'Fish (Poisson)',
        'description': 'Forme de poisson - 4 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-circle',
        'color': 'info',
        'count': 4
    },
    'oll-knight': {
        'name': 'Knight (Cavalier)',
        'description': 'Mouvement de cavalier - 8 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-bezier2',
        'color': 'primary',
        'count': 8
    },
    'oll-awkward': {
        'name': 'Awkward (Étranges)',
        'description': 'Cas inhabituels - 4 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-question-circle',
        'color': 'secondary',
        'count': 4
    },
    'oll-t-shape': {
        'name': 'T-Shape (Forme T)',
        'description': 'Forme en T - 2 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-align-center',
        'color': 'success',
        'count': 2
    },
    'oll-c-shape': {
        'name': 'C-Shape (Forme C)',
        'description': 'Forme en C - 2 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-moon',
        'color': 'primary',
        'count': 2
    },
    'oll-w-shape': {
        'name': 'W-Shape (Forme W)',
        'description': 'Forme en W - 2 cas',
        'slug_prefix': 'oll-',
        'icon': 'bi-arrow-down-up',
        'color': 'info',
        'count': 2
    },
}

# ============================================================================
# PLL CATEGORIES (21 cases total)
# ============================================================================
PLL_CATEGORIES = {
    'pll-solved': {
        'name': 'Solved (Résolu)',
        'description': 'Cube complètement résolu - Aucun PLL nécessaire',
        'slug_prefix': 'pll-solved',
        'icon': 'bi-check-circle-fill',
        'color': 'success',
        'count': 1
    },
    'pll-edges-only': {
        'name': 'Edges Only (Arêtes seulement)',
        'description': 'Permutation des arêtes uniquement - Ua, Ub, H, Z (4 cas)',
        'slug_prefix': 'pll-',
        'icon': 'bi-arrows-move',
        'color': 'primary',
        'count': 4
    },
    'pll-adjacent-swap': {
        'name': 'Adjacent Swap (Échange adjacent)',
        'description': 'Échange de pièces adjacentes - T, J, F, R, G perms (12 cas)',
        'slug_prefix': 'pll-',
        'icon': 'bi-arrow-left-right',
        'color': 'info',
        'count': 12
    },
    'pll-diagonal-swap': {
        'name': 'Diagonal Swap (Échange diagonal)',
        'description': 'Échange de pièces diagonales - Y, V, N perms (4 cas)',
        'slug_prefix': 'pll-',
        'icon': 'bi-x-lg',
        'color': 'warning',
        'count': 4
    },
}


# ============================================================================
# OLL VIEW
# ============================================================================
def cfop_oll_view(request, category=None):
    """
    Display OLL cases with category filtering
    Similar structure to F2L view
    """
    print(f"🔍 OLL view called with category: {category}")

    # Get all OLL cases
    all_cases = CubeState.objects.filter(
        method='cfop', 
        slug__startswith='oll-'
    ).order_by('step_number')
    
    print(f"📊 Found {all_cases.count()} OLL cases")


    # Determine which category to show
    current_category = category if category in OLL_CATEGORIES else None
    
    if current_category:
        # Filter by specific category
        filtered_cases = all_cases.filter(category=current_category)
        page_title = OLL_CATEGORIES[current_category]['name']
        page_description = OLL_CATEGORIES[current_category]['description']
    else:
        # Show cross (solved) by default - just case #1
        filtered_cases = all_cases.filter(slug='oll-01')
        page_title = "OLL - Orientation de la Dernière Couche"
        page_description = "Orientation of Last Layer - 57 cas pour orienter tous les stickers du dessus"
    
    # Prepare categories with active state and counts
    categories_with_counts = {}
    for cat_key, cat_info in OLL_CATEGORIES.items():
        count = all_cases.filter(category=cat_key).count()
        categories_with_counts[cat_key] = {
            **cat_info,
            'actual_count': count,
            'is_active': cat_key == current_category
        }
    
    # Statistics
    total_cases = all_cases.count()
    easy_cases = all_cases.filter(difficulty='facile').count()
    medium_cases = all_cases.filter(difficulty='moyen').count()
    hard_cases = all_cases.filter(difficulty='difficile').count()
    
    context = {
        'page_title': page_title,
        'page_description': page_description,
        'cases': filtered_cases,
        'categories': categories_with_counts,
        'current_category': current_category,
        'total_cases': total_cases,
        'easy_cases': easy_cases,
        'medium_cases': medium_cases,
        'hard_cases': hard_cases,
        'method': 'OLL',
        'method_full': 'Orientation of Last Layer',
    }
    
    return render(request, 'francontcube/methods/cfop/oll_view.html', context)


# ============================================================================
# PLL VIEW
# ============================================================================
def cfop_pll_view(request, category=None):
    """
    Display PLL cases with category filtering
    Similar structure to F2L and OLL views
    """
    # Get all PLL cases
    all_cases = CubeState.objects.filter(
        method='cfop', 
        slug__startswith='pll-'
    ).order_by('step_number')
    
    # Determine which category to show
    current_category = category if category in PLL_CATEGORIES else None
    
    if current_category:
        # Filter by specific category
        filtered_cases = all_cases.filter(category=current_category)
        page_title = PLL_CATEGORIES[current_category]['name']
        page_description = PLL_CATEGORIES[current_category]['description']
    else:
        # Show solved by default
        filtered_cases = all_cases.filter(slug='pll-solved')
        page_title = "PLL - Permutation de la Dernière Couche"
        page_description = "Permutation of Last Layer - 21 cas pour permuter les pièces de la dernière couche"
    
    # Prepare categories with active state and counts
    categories_with_counts = {}
    for cat_key, cat_info in PLL_CATEGORIES.items():
        count = all_cases.filter(category=cat_key).count()
        categories_with_counts[cat_key] = {
            **cat_info,
            'actual_count': count,
            'is_active': cat_key == current_category
        }
    
    # Statistics
    total_cases = all_cases.count()
    easy_cases = all_cases.filter(difficulty='facile').count()
    medium_cases = all_cases.filter(difficulty='moyen').count()
    hard_cases = all_cases.filter(difficulty='difficile').count()
    
    context = {
        'page_title': page_title,
        'page_description': page_description,
        'cases': filtered_cases,
        'categories': categories_with_counts,
        'current_category': current_category,
        'total_cases': total_cases,
        'easy_cases': easy_cases,
        'medium_cases': medium_cases,
        'hard_cases': hard_cases,
        'method': 'PLL',
        'method_full': 'Permutation of Last Layer',
    }
    
    return render(request, 'francontcube/methods/cfop/pll_view.html', context)


# ============================================================================
# INDIVIDUAL CASE DETAIL VIEWS
# ============================================================================
def oll_case_detail(request, slug):
    """
    Display detailed view of a single OLL case with Roofpig animation
    """
    from django.shortcuts import get_object_or_404
    
    cube_state = get_object_or_404(CubeState, slug=slug, method='cfop')
    
    # Get next and previous cases in the same category
    same_category = CubeState.objects.filter(
        method='cfop',
        category=cube_state.category
    ).order_by('step_number')
    
    current_index = list(same_category.values_list('id', flat=True)).index(cube_state.id)
    
    next_case = same_category[current_index + 1] if current_index < len(same_category) - 1 else None
    prev_case = same_category[current_index - 1] if current_index > 0 else None
    
    context = {
        'cube_state': cube_state,
        'page_title': cube_state.name,
        'roofpig_config': cube_state.get_roofpig_config(),
        'next_case': next_case,
        'prev_case': prev_case,
        'category_info': OLL_CATEGORIES.get(cube_state.category, {}),
        'method': 'OLL',
    }
    
    return render(request, 'francontcube/methods/cfop/case_detail.html', context)


def pll_case_detail(request, slug):
    """
    Display detailed view of a single PLL case with Roofpig animation
    """
    from django.shortcuts import get_object_or_404
    
    cube_state = get_object_or_404(CubeState, slug=slug, method='cfop')
    
    # Get next and previous cases in the same category
    same_category = CubeState.objects.filter(
        method='cfop',
        category=cube_state.category
    ).order_by('step_number')
    
    current_index = list(same_category.values_list('id', flat=True)).index(cube_state.id)
    
    next_case = same_category[current_index + 1] if current_index < len(same_category) - 1 else None
    prev_case = same_category[current_index - 1] if current_index > 0 else None
    
    context = {
        'cube_state': cube_state,
        'page_title': cube_state.name,
        'roofpig_config': cube_state.get_roofpig_config(),
        'next_case': next_case,
        'prev_case': prev_case,
        'category_info': PLL_CATEGORIES.get(cube_state.category, {}),
        'method': 'PLL',
    }
    
    return render(request, 'francontcube/methods/cfop/case_detail.html', context)

def test_oll_view(request):
    from django.http import HttpResponse
    from cube.models import CubeState
    
    oll_cases = CubeState.objects.filter(slug__startswith='oll-')
    html = f"<h1>OLL Test</h1><p>Found {oll_cases.count()} cases:</p><ul>"
    for case in oll_cases:
        html += f"<li>{case.name} - {case.category}</li>"
    html += "</ul>"
    return HttpResponse(html)