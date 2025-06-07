# core/middleware/disable_strumsphere.py

from django.http import HttpResponseForbidden
from django.shortcuts import render

class DisableStrumSphereMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/StrumSphere/"):
            return render(request, "songbook/strumsphere_disabled.html", status=403)
        return self.get_response(request)