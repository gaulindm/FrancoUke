from django.urls import path
#from francontcube.views.cfop.f2l import cfop, cfop_f2l_basic

from . import views

app_name = "francontcube"

urlpatterns = [
    # ============================================================
    # HOME & LEGACY
    # ============================================================
    path("", views.home, name="home"),
    path("slides/", views.slides, name="slides"),
    path("pdfs/", views.pdfs, name="pdfs"),
    path("videos/", views.videos, name="videos"),
    path("ressources3par3/", views.ressources3par3, name="ressources3par3"),
    
    # ============================================================
    # CUBIE NEWBIE METHOD
    # ============================================================
    path('methods/cubienewbie/', views.method_cubienewbie, name='method_cubienewbie'),
    path('methods/cubienewbie/about/', views.cubienewbie_about, name='cubienewbie_about'),
    path('methods/cubienewbie/cube/', views.cubienewbie_cube_intro, name='cubienewbie_cube_intro'),
    path('methods/cubienewbie/notation/', views.cubienewbie_notation, name='cubienewbie_notation'),
    path('methods/cubienewbie/daisy/', views.cubienewbie_daisy, name='cubienewbie_daisy'),
    path('methods/cubienewbie/white-cross/', views.cubienewbie_white_cross, name='cubienewbie_white_cross'),
    path('methods/cubienewbie/bottom-corners/', views.cubienewbie_bottom_corners, name='cubienewbie_bottom_corners'),
    path('methods/cubienewbie/second-layer/', views.cubienewbie_second_layer, name='cubienewbie_second_layer'),
    path('methods/cubienewbie/yellow-cross/', views.cubienewbie_yellow_cross, name='cubienewbie_yellow_cross'),
    path('methods/cubienewbie/yellow-face/', views.cubienewbie_yellow_face, name='cubienewbie_yellow_face'),
    path('methods/cubienewbie/corner-permutation/', views.cubienewbie_corner_permutation, name='cubienewbie_corner_permutation'),
    path('methods/cubienewbie/edge-permutation/', views.cubienewbie_edge_permutation, name='cubienewbie_edge_permutation'),
    
    # ============================================================
    # BEGINNER METHOD
    # ============================================================
    path('methods/beginner/', views.beginner_method, name='method_beginner'),
    path('methods/beginner/about/', views.beginner_about, name='beginner_about'),
    path('methods/beginner/white-cross/', views.beginner_white_cross, name='beginner_white_cross'),
    path('methods/beginner/bottom-corners/', views.beginner_bottom_corners, name='beginner_bottom_corners'),
    path('methods/beginner/second-layer/', views.beginner_second_layer, name='beginner_second_layer'),
    path('methods/beginner/yellow-cross/', views.beginner_yellow_cross, name='beginner_yellow_cross'),
    path('methods/beginner/yellow-face/', views.beginner_yellow_face, name='beginner_yellow_face'),
    path('methods/beginner/corner-permutation/', views.beginner_corner_permutation, name='beginner_corner_permutation'),
    path('methods/beginner/edge-permutation/', views.beginner_edge_permutation, name='beginner_edge_permutation'),
    
    # ============================================================
    # CFOP METHOD
    # ============================================================
    path('methods/cfop/', views.method_cfop, name='method_cfop'),
    #path('methods/cfop/', cfop, name='method_cfop'),  # ← Use imported cfop directly
    path('methods/cfop/about/', views.cfop_about, name='cfop_about'),
    path('methods/cfop/cross/', views.cfop_cross, name='cfop_cross'),
    path('methods/cfop/f2l/', views.cfop_f2l, name='cfop_f2l'),
    path('methods/cfop/f2l/basic/', views.cfop_f2l_basic, name='cfop_f2l_basic'),

    #path('methods/cfop/f2l/basic/', cfop_f2l_basic, name='cfop_f2l_basic'),  # ← Use imported function
    path('methods/cfop/oll/', views.cfop_oll, name='cfop_oll'),
    path('methods/cfop/pll/', views.cfop_pll, name='cfop_pll'),

    # ============================================================
    # OTHER METHODS (legacy - to be migrated)
    # ============================================================
    path('methods/f2l/', views.method_f2l, name='method_f2l'),
    path('methods/roux/', views.method_roux, name='method_roux'),
]