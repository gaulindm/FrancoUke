# board/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    full_board_view,
    rehearsal_detail_view,
    board_item_gallery_view,
    item_photo_list,
    availability_matrix,
    performer_event_list,
    create_board_message,
    update_event_availability,
    BoardItemViewSet,
    EventViewSet,
)

app_name = "board"  # used for {% url 'board:...' %}

# --- DRF Router setup ---
router = DefaultRouter()
router.register(r"items", BoardItemViewSet)
router.register(r"events", EventViewSet)

# --- URL Patterns ---
urlpatterns = [
    path("", full_board_view, name="full_board"),

    # Board Items
    path("rehearsal/<int:pk>/", rehearsal_detail_view, name="rehearsal_detail"),
    path("item/<int:item_id>/gallery/", board_item_gallery_view, name="item_gallery"),
    path("api/items/<int:item_id>/photos/", item_photo_list, name="item_photo_list"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),

    # Availability
    path("availability-matrix/", availability_matrix, name="availability_matrix"),
    path("availability/<int:event_id>/", update_event_availability, name="set_event_availability"),

    # Performers
    path("performances/", performer_event_list, name="performer_event_list"),

    # Messages
    path("column/<int:column_id>/messages/new/", create_board_message, name="create_board_message"),

    # REST API routes
    path("api/", include(router.urls)),
]
