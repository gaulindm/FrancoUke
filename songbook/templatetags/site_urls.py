from django import template

register = template.Library()  # ✅ Required to define tags

@register.simple_tag(takes_context=True)
def site_url(context, name):
    """
    Safely build namespaced URL.
    Falls back to the un-namespaced version if namespace is missing.
    """
    ns = context.get("site_namespace", "")
    if ns:
        return f"{ns}:{name}"
    return name
