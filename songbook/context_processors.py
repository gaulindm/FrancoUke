def site_context(request):
    """Inject site-related variables based on URL namespace."""
    ns = getattr(request.resolver_match, "namespace", "") if request.resolver_match else ""
    site_map = {
        "francouke":  ("FrancoUke", "base_francouke.html"),
        "strumsphere": ("StrumSphere", "base_strumsphere.html"),
        "uke4ia":     ("Uke4ia", "base_uke4ia.html"),
    }

    site_name, base_template = site_map.get(ns, ("FrancoUke", "base_francouke.html"))

    return {
        "site_name": site_name,
        "site_namespace": ns,
        "base_template": base_template,
    }
