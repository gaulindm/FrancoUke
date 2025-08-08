from django.urls import path
from . import views
from .views import board_item_gallery_view, item_photo_list

urlpatterns = [
    path('', views.full_board_view, name='full_board'),
    path('update-card/', views.update_card_position, name='update_card_position'),  # 👈 This line
    path('availability/', views.update_availability, name='update_availability'),  # 👈 availability update
    path('rehearsal/<int:pk>/', views.rehearsal_detail_view, name='rehearsal_detail'),  # 👈 new detail route
    path('item/<int:item_id>/gallery/', board_item_gallery_view, name='item_gallery'),
    path('api/items/<int:item_id>/photos/', item_photo_list, name='item_photo_list'),


]
