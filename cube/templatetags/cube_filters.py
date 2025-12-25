from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def parse_algorithm(algorithm_string):
    """Parse algorithm string and return SVG icons HTML"""
    if not algorithm_string or algorithm_string.strip() == '':
        return ''
    
    # Split by spaces and filter out empty strings
    moves = algorithm_string.strip().split()
    
    # Convert each move to SVG
    svg_list = []
    for move in moves:
        # Convert notation: R' -> R-prime, R2 -> R2, R -> R
        svg_id = move.replace("'", "-prime").replace("2", "2")
        svg_list.append(f'<svg class="move-icon"><use href="#{svg_id}"/></svg>')
    
    return mark_safe('\n                            '.join(svg_list))