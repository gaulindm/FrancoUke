def site_namespace(request):
    path = request.path

    if path.startswith("/FrancoUke/"):
        return {
            "site_name": "FrancoUke",
            "site_namespace": "francouke",
        }
    elif path.startswith("/StrumSphere/"):
        return {
            "site_name": "StrumSphere",
            "site_namespace": "strumsphere",
        }

    return {
        "site_name": "FrancoUke",
        "site_namespace": "francouke",
    }
