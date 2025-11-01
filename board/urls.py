# board/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    full_board_view,
    rehearsal_detail_view,
    board_item_gallery_view,
    item_photo_list,
    availability_matrix,
    performer_event_list,
    create_board_message,
    update_event_availability,
    event_detail,
    BoardItemViewSet,
    EventViewSet,
)

app_name = "board"

router = DefaultRouter()
router.register(r"items", BoardItemViewSet, basename="boarditem")
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    path("", full_board_view, name="full_board"),

    # Board Items
    path("rehearsal/<int:pk>/", rehearsal_detail_view, name="rehearsal_detail"),
    path("item/<int:item_id>/gallery/", board_item_gallery_view, name="board_item_gallery"),
    path("api/items/<int:item_id>/photos/", item_photo_list, name="item_photo_list"),

    # Events
    path("event/<int:event_id>/", event_detail, name="event_detail"),

    # ✅ Unified availability route
    path(
        "event/<int:event_id>/availability/",
        update_event_availability,
        name="set_event_availability",  # keep this name for template compatibility
    ),

    # Performers
    path("performances/", performer_event_list, name="performer_event_list"),

    # Availability Matrix
    path("availability-matrix/", availability_matrix, name="availability_matrix"),

    # Messages
    path("column/<int:column_id>/messages/new/", create_board_message, name="create_board_message"),

    # API
    path("api/", include(router.urls)),
]
