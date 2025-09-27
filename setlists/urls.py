from django.urls import path
from . import views

app_name = "setlists"

urlpatterns = [
    path("", views.setlist_list, name="list"),
    path("<int:pk>/", views.setlist_detail, name="detail"),
    path(
        "<int:setlist_id>/teleprompter/<int:order>/",
        views.setlist_teleprompter,
        name="setlist_teleprompter",
    ),
    path("export/<int:pk>/", views.export_setlist, name="export"),
    path("import/", views.import_setlist, name="import"),

]
