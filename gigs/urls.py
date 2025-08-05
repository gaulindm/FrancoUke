from django.urls import path
from . import views

app_name = "gigs"

urlpatterns = [
    # Landing page
    path("", views.gig_home, name="home"),

    # Gigs listing
    path("gigs/", views.gig_list, name="gig_list"),
    
    path('calendar/<int:gig_id>/', views.add_to_calendar, name='add_to_calendar'),


    # Optional: Gig detail (future-proofing)
    # path("gigs/<int:gig_id>/", views.gig_detail, name="gig_detail"),

    # Availability pages
    path("my-availability/", views.my_availability, name="my_availability"),
    path("matrix/", views.availability_matrix, name="availability_matrix"),
]
