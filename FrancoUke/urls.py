from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from core.views import landing_page 
from public import views as public_views

urlpatterns = [
    path("admin/assets/", include("assets.urls")),  # ✅ mount assets under /admin/assets/
    path("admin/", admin.site.urls),

    path("users/", include("users.urls")),

    # Root landing page
    path('', landing_page, name='landing'),

    # Board (Trello-style UI)
    path('board/', include('board.urls')),

    path('teleprompter/', include('teleprompter.urls', namespace='teleprompter')),
    path('tinymce/', include('tinymce.urls')),

    path("setlists/", include("setlists.urls", namespace="setlists")),

#    path("assets/", include("assets.urls", namespace="asset_repo")),  # ✅ add this line



    # Songbooks
    path("francouke/", include(("songbook.urls", "songbook"), namespace="francouke")),
    path("strumsphere/", include(("songbook.urls", "songbook"), namespace="strumsphere")),

    # Public site pages
    path("about/", public_views.about, name="about"),
    path("public-board/", public_views.public_board, name="public_board"),
    path("contact/", public_views.contact, name="contact"),

   #nouvel application pour le cube mosaic
    path('cube_prep/', include('cube_prep.urls')),  # 👈 new line

    #nouvel application pour le site francontcube
    path("francontcube/", include("francontcube.urls")),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Media & static support (for dev)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
