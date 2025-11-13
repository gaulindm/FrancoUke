from django.urls import path
from . import views

urlpatterns = [
    path('', views.generator_home, name='cube_home'),
    path('generate/', views.generate_single_card, name='generate_single_scramble'),  # ✅ match view function
    path('generate_two/', views.generate_two_cards_view, name='generate_two_cards'),
]
