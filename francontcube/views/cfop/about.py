"""
About page for CFOP method.
"""

from ..base import StepView


class AboutView(StepView):
    """About CFOP method page."""
    
    template_name = "francontcube/methods/cfop/about.html"
    method_name = "CFOP"
    step_name = "À propos"
    step_icon = "info-circle"
    
    cube_state_slugs = {}


# Export
about = AboutView.as_view()