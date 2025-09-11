from django.urls import path
from . import views

app_name = 'teleprompter'

urlpatterns = [
    path('song/<int:song_id>/', views.show, name='show'),
]
