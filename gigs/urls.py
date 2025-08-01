from django.urls import path
from . import views

app_name = "gigs"



urlpatterns = [
    path("my-availability/", views.my_availability, name="my_availability"),
    path('matrix/', views.availability_matrix, name='availability_matrix'),
]
