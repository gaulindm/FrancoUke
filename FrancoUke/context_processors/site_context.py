def site_context(request):
    site_name = "FrancoUke" if "FrancoUke" in request.path else "StrumSphere"
    site_namespace = "francouke" if site_name == "FrancoUke" else "strumsphere"
    
    return {
        "site_name": site_name,
        "site_namespace": site_namespace,
    }
