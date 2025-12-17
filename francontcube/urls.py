from django.urls import path
from . import views



app_name = "francontcube"

urlpatterns = [
    path("", views.home, name="home"),
    path("slides/", views.slides, name="slides"),
    path("pdfs/", views.pdfs, name="pdfs"),
    path("videos/", views.videos, name="videos"),
    path("ressources3par3/", views.ressources3par3, name="ressources3par3"),
      # Cubie Newbie Method
    path('methods/cubienewbie/', views.method_cubienewbie, name='method_cubienewbie'),
    path('methods/cubienewbie/daisy/', views.daisy, name='daisy'),
    path('methods/cubienewbie/notation/', views.notation, name='notation'),
    path('methods/cubienewbie/white-cross/', views.white_cross, name='white_cross'),
    path('methods/cubienewbie/bottom-corners/', views.bottom_corners, name='bottom_corners'),
    path('methods/cubienewbie/second-layer/', views.second_layer, name='second_layer'),
    path('methods/cubienewbie/yellow-cross/', views.yellow_cross, name='yellow_cross'),
    path('methods/cubienewbie/yellow-face/', views.yellow_face, name='yellow_face'),
    path('methods/cubienewbie/corner-permutation/', views.corner_permutation, name='corner_permutation'),
    path('methods/cubienewbie/edge-permutation/', views.edge_permutation, name='edge_permutation'),
    
    # Other Methods (coming soon)
    path('methods/beginner/', views.method_beginner, name='method_beginner'),
    path('methods/f2l/', views.method_f2l, name='method_f2l'),
    path('methods/roux/', views.method_roux, name='method_roux'), #path("methode/", views.debutante, name="debutante"),

    # 👇 Les méthodes et etapes



]
