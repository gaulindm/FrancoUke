"""
URL configuration for FrancoUke project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from django.http import HttpResponse
from songbook import views

# Optional: Friendly disabled message
def strumsphere_disabled(request, *args, **kwargs):
    return HttpResponse("StrumSphere is currently not active. Please visit FrancoUke.", status=403)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # ✅ Ensure the user URLs are included properly
    path('', include('songbook.urls')),
        # Active site: FrancoUke
    path("FrancoUke/", views.home, name="home"),
    path("FrancoUke/song/new/", views.SongCreateView.as_view(), name="song-create"),
    path("FrancoUke/song/<int:pk>/", views.ScoreView.as_view(), name="score-view"),
]

# Toggle StrumSphere availability
if getattr(settings, "ENABLE_STRUMSPHERE", False):
    urlpatterns += [
        path("StrumSphere/", include("songbook.urls")),
    ]
else:
    urlpatterns += [
        path("StrumSphere/", strumsphere_disabled),
        path("StrumSphere/<path:extra>", strumsphere_disabled),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)