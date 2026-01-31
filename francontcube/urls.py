from django.urls import path

# Import organized views
from . import views

# CFOP specific imports (for clarity and organization)
from francontcube.views.cfop.f2l import cfop, cfop_f2l_basic
from francontcube.views.cfop.oll_pll import (
    cfop_oll_view,
    cfop_pll_view,
    oll_case_detail,
    pll_case_detail,
)
from francontcube.views.cfop.two_look_oll import two_look_oll_view
from francontcube.views.cfop.two_look_pll import two_look_pll_view
from francontcube.views.cfop.beginner_to_f2l import beginner_to_f2l_bridge

# ⚠️ CORRECTION: Les vues d'introduction doivent être importées depuis leurs propres fichiers
# PAS depuis oll_pll.py
from francontcube.views.cfop.f2l_intro import cfop_f2l_intro
from francontcube.views.cfop.oll_intro import cfop_oll_intro
from francontcube.views.cfop.pll_intro import cfop_pll_intro

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
    # Main pages
    path('methods/cfop/', views.method_cfop, name='method_cfop'),
    path('methods/cfop/about/', views.cfop_about, name='cfop_about'),
    path('methods/cfop/cross/', views.cfop_cross, name='cfop_cross'),
    path('methods/cfop/beginner-to-f2l/', beginner_to_f2l_bridge, name='beginner_to_f2l'),

    # ──────────────────────────────────────────────────────────
    # F2L Routes
    # ──────────────────────────────────────────────────────────
    # ⚠️ ORDRE IMPORTANT: Plus spécifique d'abord!
    
    # 1. Introduction (plus spécifique)
    path('methods/cfop/f2l/introduction/', cfop_f2l_intro, name='cfop_f2l_intro'),
    
    # 2. Basic cases (spécifique aussi)
    path('methods/cfop/f2l/basic/', views.cfop_f2l_basic, name='cfop_f2l_basic'),
    
    # 3. Catégorie générique (moins spécifique, en dernier)
    path('methods/cfop/f2l/<str:category>/', cfop_f2l_basic, name='cfop_f2l_category'),
    
    # ──────────────────────────────────────────────────────────
    # OLL Routes
    # ──────────────────────────────────────────────────────────
    # ⚠️ ORDRE IMPORTANT: Plus spécifique d'abord!
    
    # 1. 2-Look OLL (très spécifique)
    path('methods/cfop/oll/2-look/', two_look_oll_view, name='two_look_oll'),
    
    # 2. Introduction (spécifique)
    path('methods/cfop/oll/introduction/', cfop_oll_intro, name='cfop_oll_intro'),
    
    # 3. Cas détaillé avec slug (spécifique avec prefix 'case/')
    path('methods/cfop/oll/case/<slug:slug>/', oll_case_detail, name='oll_case_detail'),
    
    # 4. Vue par catégorie (moins spécifique)
    path('methods/cfop/oll/<str:category>/', cfop_oll_view, name='cfop_oll_category'),
    
    # 5. Vue générale (la moins spécifique, en dernier)
    path('methods/cfop/oll/', cfop_oll_view, name='cfop_oll'),
    
    # ──────────────────────────────────────────────────────────
    # PLL Routes
    # ──────────────────────────────────────────────────────────
    # ⚠️ ORDRE IMPORTANT: Plus spécifique d'abord!
    
    # 1. 2-Look PLL (très spécifique)
    path('methods/cfop/pll/2-look/', two_look_pll_view, name='two_look_pll'),
    
    # 2. Introduction (spécifique)
    path('methods/cfop/pll/introduction/', cfop_pll_intro, name='cfop_pll_intro'),
    
    # 3. Cas détaillé avec slug (spécifique avec prefix 'case/')
    path('methods/cfop/pll/case/<slug:slug>/', pll_case_detail, name='pll_case_detail'),
    
    # 4. Vue par catégorie (moins spécifique)
    path('methods/cfop/pll/<str:category>/', cfop_pll_view, name='cfop_pll_category'),
    
    # 5. Vue générale (la moins spécifique, en dernier)
    path('methods/cfop/pll/', cfop_pll_view, name='cfop_pll'),

    # ============================================================
    # OTHER METHODS (legacy - to be migrated)
    # ============================================================
    path('methods/f2l/', views.method_f2l, name='method_f2l'),
    path('methods/roux/', views.method_roux, name='method_roux'),
]