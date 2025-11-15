from django.urls import path
from . import views

urlpatterns = [
    path('', views.generator_home, name='cube_home'),
    path('generate_three_cards/', views.generate_three_cards_view, name='generate_three_cards'),
    path('color-matrix/', views.color_matrix_view, name='color_matrix'),
    path('save-mosaic/', views.save_mosaic, name='save-mosaic'),
    path('cube-face-moves/', views.cube_face_moves_view, name='cube_face_moves'),

]
