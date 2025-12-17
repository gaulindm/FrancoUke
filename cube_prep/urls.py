from django.urls import path
from . import views

app_name = "cube_prep"

urlpatterns = [
    path('', views.generator_home, name='cube_prep'),
    path('generate_three_cards/', views.generate_three_cards_view, name='generate_three_cards'),
    path('color-matrix/', views.color_matrix_view, name='color_matrix'),
    path('save-mosaic/', views.save_mosaic, name='save-mosaic'),
    path('cube-face-moves/', views.cube_face_moves_view, name='cube_face_moves'),
    #path('generate-cube-pdf/<int:cube_id>/', views.generate_cube_pdf_view, name='generate_cube_pdf'),
    path('pdf-generator/', views.pdf_generator_view, name='pdf_generator_view'),
    path('pdf-generator/download/', views.generate_three_copies_pdf, name='generate_three_copies_pdf'),

]
