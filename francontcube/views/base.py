#francontcube/views/base.py
"""
Base utilities for Francontcube views.

Provides reusable classes and functions for:
- Loading cube states safely with error tracking
- Building breadcrumbs consistently
- Creating step tutorial views with minimal boilerplate
"""

from django.shortcuts import render
from cube.models import CubeState


class CubeStateLoader:
    """
    Utility class for loading cube states safely with error tracking.
    """
    
    @staticmethod
    def get_safe(slug):
        """
        Safely get a single cube state.
        
        Args:
            slug: The slug of the CubeState to load
            
        Returns:
            CubeState object or None if not found
        """
        try:
            return CubeState.objects.get(slug=slug)
        except CubeState.DoesNotExist:
            return None
    
    @staticmethod
    def get_multiple(slug_dict):
        """
        Load multiple cube states safely.
        
        Args:
            slug_dict: Dict mapping context variable names to slugs
                      e.g., {'goal_state': 'marguerite-goal', 'before_state': 'marguerite-before'}
            
        Returns:
            Tuple of (states_dict, missing_slugs)
            - states_dict: Dict with same keys as input, values are json_state or None
            - missing_slugs: List of slugs that weren't found
        """
        states = {}
        missing = []
        
        for key, slug in slug_dict.items():
            state = CubeStateLoader.get_safe(slug)
            states[key] = state.json_state if state else None
            if state is None:
                missing.append(slug)
        
        return states, missing


class StepView:
    """
    Base class for step tutorial views.
    
    Handles common patterns like breadcrumbs and cube state loading.
    Subclasses just need to define configuration attributes.
    
    Example:
        class DaisyView(StepView):
            template_name = "francontcube/methods/cubienewbie/daisy.html"
            step_name = "La Marguerite"
            step_icon = "flower3"
            cube_state_slugs = {
                'goal_state': 'marguerite-goal',
                'before_state': 'marguerite-before',
                'after_state': 'marguerite-after',
            }
        
        # In urls.py:
        path('daisy/', DaisyView.as_view(), name='daisy')
    """
    
    # Configuration - subclasses should override these
    template_name = None
    method_name = "Apprenti Cubi"
    step_name = None
    step_number = None
    step_icon = None
    cube_state_slugs = {}  # Dict of {context_key: slug}

    # Navigation - subclasses can override these  # ← NOUVEAU
    next_step = None  # URL name for next step
    prev_step = None  # URL name for previous step
    
    @classmethod
    def as_view(cls):
        """
        Return a view function suitable for URL routing.
        
        Returns:
            View function that takes (request) and returns HttpResponse
        """
        def view(request):
            instance = cls()
            return instance.render(request)
        return view
    
    def get_breadcrumbs(self):
        """
        Generate breadcrumbs for this step.
        
        Returns:
            List of breadcrumb dicts with 'name', 'url', and 'icon'
        """
        return [
            {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
            {'name': self.method_name, 'url': self.get_method_url(), 'icon': 'star-fill'},
            {'name': self.step_name, 'url': '', 'icon': self.step_icon},
        ]
    
    def get_method_url(self):
        """
        Get URL for method overview page.
        
        Returns:
            URL string for the method's main page
        """
        method_urls = {
            'Apprenti Cubi': 'francontcube:method_cubienewbie',
            'Débutant': 'francontcube:method_beginner',
            'CFOP': 'francontcube:method_cfop',  # ← AJOUTER
            'Roux': 'francontcube:method_roux',
        }
        
        url_name = method_urls.get(self.method_name)
        if url_name:
            try:
                return reverse(url_name)
            except:
                return '/francontcube/'
        return '/francontcube/'
    
    def get_context_data(self):
        """Get context data for template."""
        states, missing = CubeStateLoader.get_multiple(self.cube_state_slugs)
        
        context = {
            'breadcrumbs': self.get_breadcrumbs(),
            'missing_slugs': missing,
            **states,
        }
        
        # Add navigation if defined  # ← NOUVEAU
        if self.step_number is not None:
            context['step_number'] = self.step_number
        if self.next_step:
            context['next_step'] = self.next_step
        if self.prev_step:
            context['prev_step'] = self.prev_step
        
        return context
    
    def render(self, request):
        """
        Render the template with context.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            HttpResponse with rendered template
        """
        if self.template_name is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define template_name"
            )
        
        return render(request, self.template_name, self.get_context_data())


def build_breadcrumbs(method_name=None, step_name=None, step_icon=None):
    """
    Legacy helper function for building breadcrumbs.
    
    Kept for backward compatibility with views that haven't been migrated
    to the StepView class yet.
    
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