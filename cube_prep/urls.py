from django.urls import path
from . import views

app_name = "cube_prep"

urlpatterns = [
    path('', views.generator_home, name='cube_prep'),
    path('mosaics/', views.mosaic_list, name='mosaic_list'),
    path("teacher-pdf/", views.teacher_pdf, name="teacher_pdf"),

    path('mosaics/<int:mosaic_id>/', views.mosaic_detail, name='mosaic_detail'),
    path('save-mosaic/', views.save_mosaic, name='save_mosaic'),
    #path('generate_three_cards/', views.generate_three_cards_view, name='generate_three_cards'),
    path('color-matrix/', views.color_matrix_view, name='color_matrix'),
    #path('cube-face-moves/', views.cube_face_moves_view, name='cube_face_moves'),
    #path('generate-cube-pdf/<int:cube_id>/', views.generate_cube_pdf_view, name='generate_cube_pdf'),
    #path('pdf-generator/', views.pdf_generator_view, name='pdf_generator_view'),
    #path('pdf-generator/download/', views.generate_three_copies_pdf, name='generate_three_copies_pdf'),

]
