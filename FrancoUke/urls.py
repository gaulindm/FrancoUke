from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from core.views import landing_page 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),

    # Redirect root to FrancoUke
    #path("", lambda request: redirect("francouke:home")),
    path('', landing_page, name='landing'),



    # Songbooks
    path("francouke/", include(("songbook.urls", "songbook"), namespace="francouke")),
    path("strumsphere/", include(("songbook.urls", "songbook"), namespace="strumsphere")),

    # Gigs / Uke4ia
    path("uke4ia/", include(("gigs.urls", "gigs"), namespace="uke4ia")),

    # Optional shortcut to gig list
    path("gigs/", lambda request: redirect("uke4ia:gig_list")),

    
]



# 🛠 Static/media support in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
