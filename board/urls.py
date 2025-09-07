from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    BoardItemViewSet,
    EventViewSet,
    board_item_gallery_view,
    item_photo_list, update_event_availability
)

# DRF Router
router = DefaultRouter()
#router.register(r"performances", views.PerformanceViewSet)
router.register(r"items", BoardItemViewSet)  # 👈 new one
router.register(r"events", EventViewSet)  # 👈 NEW


urlpatterns = [
    # Your regular Django views
    path("", views.full_board_view, name="full_board"),
    #path('availability/<int:event_id>/', update_availability, name='set_availability'),
    #path("update-card/", views.update_card_position, name="update_card_position"),
    #path("availability/", views.update_availability, name="update_availability"),
    path("rehearsal/<int:pk>/", views.rehearsal_detail_view, name="rehearsal_detail"),
    path("item/<int:item_id>/gallery/", board_item_gallery_view, name="item_gallery"),
    path("api/items/<int:item_id>/photos/", item_photo_list, name="item_photo_list"),
    #path("public/", views.public_board, name="public_board"),
    path("availability-matrix/", views.availability_matrix, name="availability_matrix"),
    path("performances/", views.performer_event_list, name="performer_event_list"),
    # Event detail (for modal)
    #path("event/<int:event_id>/", views.event_detail, name="event_detail"),

    # Update availability (AJAX)
    #path("event/<int:event_id>/availability/", views.update_event_availability, name="update_event_availability"),


     # --- Event system ---
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path("availability/<int:event_id>/", update_event_availability, name="set_event_availability"),

    # --- Performance system (legacy, will be removed later) ---
    #path('performance/<int:performance_id>/availability/', views.update_availability, name='set_performance_availability'),


    # Your DRF API endpoints
    path("api/", include(router.urls)),
]
