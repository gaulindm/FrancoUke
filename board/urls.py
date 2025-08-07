from django.urls import path
from . import views

urlpatterns = [
    path('', views.full_board_view, name='full_board'),
    path('update-card/', views.update_card_position, name='update_card_position'),  # 👈 This line
    path('availability/', views.update_availability, name='update_availability'),  # 👈 availability update
    path('rehearsal/<int:pk>/', views.rehearsal_detail_view, name='rehearsal_detail'),  # 👈 new detail route


]
