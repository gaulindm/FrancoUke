from django.urls import path
from .views import CustomLoginView, register, user_preferences_view
from django.contrib.auth import views as auth_views
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  # ✅ Ensure login has a single path
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("profile/", views.profile, name="profile"),  # 👈 New profile page

    path('preferences/', user_preferences_view, name='user_preferences'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
]
