from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from core.views import landing_page 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),

    # Root landing page
    path('', landing_page, name='landing'),

    # Board (Trello-style UI)
    path('board/', include('board.urls')),

    # Songbooks
    path("francouke/", include(("songbook.urls", "songbook"), namespace="francouke")),
    path("strumsphere/", include(("songbook.urls", "songbook"), namespace="strumsphere")),

   

]

# Media & static support (for dev)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
