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
    path('<int:gig_id>/', views.performer_gig_detail, name='performer_gig_detail'),

    # Availability pages
    path("my-availability/", views.my_availability, name="my_availability"),
    #path("matrix/", views.availability_matrix, name="availability_matrix"),
    #path('performer/gigs/', views.performer_gig_list, name='performer_gig_list'),
    path('performer/gigs/<int:gig_id>/', views.performer_gig_detail, name='performer_gig_detail'),
    path('performer/grid/', views.performer_gig_grid, name='performer_gig_grid'),
    path('performer/grid/<int:gig_id>/', views.performer_gig_grid_detail, name='performer_gig_grid_detail'),

]
