from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from core.views import landing_page 
from public import views as public_views

urlpatterns = [
    path("admin/assets/", include("assets.urls")),
    path("admin/", admin.site.urls),

    path("users/", include("users.urls")),

    path('', landing_page, name='landing'),

    path('board/<slug:group_slug>/', include(('board.urls', 'board'), namespace='board')),

    path('teleprompter/', include('teleprompter.urls', namespace='teleprompter')),
    path('tinymce/', include('tinymce.urls')),

    path("setlists/", include("setlists.urls", namespace="setlists")),

    path("francouke/", include(("songbook.urls", "songbook"), namespace="francouke")),
    path("strumsphere/", include(("songbook.urls", "songbook"), namespace="strumsphere")),

    path("about/", public_views.about, name="about"),
    path("contact/", public_views.contact, name="contact"),
    path("public-board/<slug:group_slug>/", include(("public.urls", "public"), namespace="public")),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)