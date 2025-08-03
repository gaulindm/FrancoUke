class SiteContextMixin:
    """Adds site_name, site_namespace, and base_template to context."""

    def get_site_namespace(self):
        return self.request.resolver_match.namespace or ""

    def get_site_name(self):
        ns = self.get_site_namespace()
        if ns == "francouke":
            return "FrancoUke"
        elif ns == "strumsphere":
            return "StrumSphere"
        elif ns == "uke4ia":
            return "Uke4ia"
        return "Unknown"

    def get_base_template(self):
        site_name = self.get_site_name()
        if site_name == "FrancoUke":
            return "base_francouke.html"
        elif site_name == "StrumSphere":
            return "base_strumsphere.html"
        elif site_name == "Uke4ia":
            return "base_uke4ia.html"
        return "base.html"  # fallback

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_namespace"] = self.get_site_namespace()
        context["site_name"] = self.get_site_name()
        context["base_template"] = self.get_base_template()
        return context
