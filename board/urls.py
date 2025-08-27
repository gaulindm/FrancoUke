from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    BoardItemViewSet,
    EventViewSet,
    board_item_gallery_view,
    item_photo_list, update_availability
)

# DRF Router
router = DefaultRouter()
#router.register(r"performances", views.PerformanceViewSet)
router.register(r"items", BoardItemViewSet)  # 👈 new one
router.register(r"events", EventViewSet)  # 👈 NEW


urlpatterns = [
    # Your regular Django views
    path("", views.full_board_view, name="full_board"),
    path('availability/<int:performance_id>/', update_availability, name='set_availability'),
    path("update-card/", views.update_card_position, name="update_card_position"),
    path("availability/", views.update_availability, name="update_availability"),
    path("rehearsal/<int:pk>/", views.rehearsal_detail_view, name="rehearsal_detail"),
    path("item/<int:item_id>/gallery/", board_item_gallery_view, name="item_gallery"),
    path("api/items/<int:item_id>/photos/", item_photo_list, name="item_photo_list"),
    path("public/", views.public_board, name="public_board"),
    path("availability-matrix/", views.availability_matrix, name="availability_matrix"),
    path("performances/", views.performer_performance_list, name="performer_performance_list"),

    # Your DRF API endpoints
    path("api/", include(router.urls)),
]
