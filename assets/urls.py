# assets/urls.py
from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("chooser/", views.asset_chooser_api, name="chooser_api"),
    path("chooser_modal/", views.chooser_modal, name="chooser_modal"),   # HTML modal

]
