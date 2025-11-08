# board/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from board import views
from .views import *  # Safe here because __init__.py controls exports


app_name = "board"

router = DefaultRouter()
router.register(r"items", BoardItemViewSet, basename="boarditem")
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    path("", full_board_view, name="full_board"),

    # Events
    path("event/<int:event_id>/", event_detail, name="event_detail"),
    path("event/<int:event_id>/availability/", update_event_availability, name="set_event_availability"),

    # Rehearsals
    path("rehearsal/<int:pk>/", rehearsal_detail_view, name="rehearsal_detail"),
    path("event/<int:event_id>/rehearsal/edit/", edit_rehearsal_details, name="edit_rehearsal_details"),
    path("event/<int:event_id>/song-notes/edit/", edit_song_rehearsal_notes, name="edit_song_rehearsal_notes"),
    path(
    "songs/<int:song_id>/rehearsal-notes/",
    views.song_rehearsal_history,
    name="song_rehearsal_history",
),


    # Performers
    path("performances/", performer_event_list, name="performer_event_list"),

    # Availability Matrix
    path("availability-matrix/", availability_matrix, name="availability_matrix"),

    # Board Items
    path("item/<int:item_id>/gallery/", board_item_gallery_view, name="board_item_gallery"),
    path("api/items/<int:item_id>/photos/", item_photo_list, name="item_photo_list"),

    # Messages
    path("column/<int:column_id>/messages/new/", create_board_message, name="create_board_message"),

    # API
    path("api/", include(router.urls)),
]
