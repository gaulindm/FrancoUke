from django.urls import path
from . import views


app_name = 'teleprompter'

urlpatterns = [
    #path("teleprompter/<int:song_id>/", views.teleprompter_view, name="teleprompter"),
    #path("<int:song_id>/", views.show, name="show"),  # ✅ name matches "show"
    path("<int:song_id>/", views.teleprompter_view, name="teleprompter"),
    path("<int:song_id>/beginner/", views.teleprompter_view, {"beginner": True}, name="teleprompter_beginner"),

]