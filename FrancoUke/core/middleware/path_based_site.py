# FrancoUke/core/middleware/path_based_site.py

from django.utils.deprecation import MiddlewareMixin
from django.contrib.sites.models import Site

class PathBasedSiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the first segment of the path (e.g. 'FrancoUke' or 'StrumSphere')
        path_root = request.path.strip("/").split("/")[0]

        try:
            # Match site based on name (case-insensitive)
            request.site = Site.objects.get(name__iexact=path_root)
        except Site.DoesNotExist:
            request.site = Site.objects.get(pk=1)  # fallback to default
