from django.urls import path
from . import views

app_name = "cube"

urlpatterns = [
    path("", views.index, name="cube-index"),
    path("icons/", views.all_icons, name="cube-all-icons"),
    path("algorithms/", views.algorithm_viewer, name="cube-algorithm-viewer"),
    path("browser/", views.browser, name="cube-browser"),
    path("view/", views.view_cube, name="view_cube"),
    path("sequence/", views.browser, name="sequence"),
    path("demo-backend-cube/", views.demo_backend_cube, name="demo_backend_cube"),
    path("demo-backend-svg/", views.demo_backend_svg, name="demo_backend_svg"),  # NEW
    path('f2l/<slug:slug>/', views.f2l_case_detail, name='f2l_case_detail'),
    path('test/top-layer/', views.test_top_layer_svg, name='test_top_layer_svg'),
    path("demo-daisy/", views.demo_daisy, name="demo_daisy"),

    # 4x4x4 routes
    path("4x4/", views.view_4x4_cube, name="view_4x4_cube"),

]
