from django.urls import path
from . import views

app_name = "setlists"

urlpatterns = [
    path("", views.setlist_list, name="list"),
    path("<int:pk>/", views.setlist_detail, name="detail"),
    path(
        "<int:setlist_id>/teleprompter/<int:order>/",
        views.setlist_teleprompter,
        name="setlist_teleprompter",
    ),
    path("export/<int:pk>/", views.export_setlist, name="export"),
    path("import/", views.import_setlist, name="import"),

    # 🧱 The missing line — Add this one:
    path("builder/", views.setlist_builder, name="setlist_builder"),
    path("builder/<int:pk>/", views.setlist_builder, name="setlist_builder"),
    path("ajax/song-search/", views.song_search, name="ajax_song_search"),

    path("event/<int:event_id>/create/", views.create_setlist_for_event, name="setlist_create_for_event"),

]
