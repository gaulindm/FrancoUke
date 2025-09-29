import logging
logger = logging.getLogger(__name__)

def site_context(request):
    ns = getattr(request.resolver_match, "namespace", "") if request.resolver_match else ""
    site_map = {
        "francouke":  ("FrancoUke", "base_francouke.html"),
        "strumsphere": ("StrumSphere", "base_strumsphere.html"),
        "uke4ia":     ("Uke4ia", "base_uke4ia.html"),
    }

    default_site = ("StrumSphere", "base_strumsphere.html")
    site_name, base_template = site_map.get(ns, default_site)

    logger.debug(f"Resolved site_context: ns={ns}, site_name={site_name}")

    return {
        "site_name": site_name,
        "site_namespace": ns,
        "base_template": base_template,
    }
