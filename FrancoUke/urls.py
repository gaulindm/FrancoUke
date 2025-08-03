from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),

    
    # 🏠 Default route redirects to FrancoUke homepage
    path("", lambda request: redirect("francouke:home")),

    # 🎵 FrancoUke routes (namespace-aware)
    path("FrancoUke/", include(("songbook.urls", "songbook"), namespace="francouke")),

    # 🎸 StrumSphere routes (namespace-aware)
    path("StrumSphere/", include(("songbook.urls", "songbook"), namespace="strumsphere")),

    # 🎸 Uke4ia routes (namespace-aware)
    path("Uke4ia/", include("gigs.urls", namespace="uke4ia")),

]



# 🛠 Static/media support in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
