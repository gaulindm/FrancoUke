from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from .models import UserPreference
from django.urls import reverse
from .forms import UserPreferenceForm
from songbook.models import SongFormatting
from .forms import CustomUserCreationForm, UserPreferenceForm  # ✅ use your custom form



class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = self.request.GET.get('site', 'FrancoUke')  # ✅ Ensure the correct site name
        return context


def register(request):
    site_name = request.GET.get("site", "FrancoUke")  # Default to FrancoUke

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)   # ✅ swapped here
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")

            messages.success(
                request,
                f'Account created for {username}! Visit your '
                f'<a href="{reverse("users:user_preferences")}?site={site_name}">'
                f'Preferences</a> page to set up your instrument choices.'
            )
            return redirect(f"/users/login/?site={site_name}")
    else:
        form = CustomUserCreationForm()   # ✅ swapped here too

    return render(request, "users/register.html", {"form": form, "site_name": site_name})


# users/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import UserPreference
from .forms import UserPreferenceForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def user_preferences_view(request):

    site_name = request.GET.get("site", "FrancoUke")
    user_pref, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserPreferenceForm(request.POST, instance=user_pref)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferences updated successfully ✔️")
            return redirect("users:user_preferences")
    else:
        form = UserPreferenceForm(instance=user_pref)

    # ✔️ Detect HTMX
    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "partials/user_preferences_modal.html",
            {"form": form, "site_name": site_name},
        )

    # ✔️ Normal request → render full page template
    return render(
        request,
        "users/user_preference_form.html",
        {"form": form, "site_name": site_name},
    )

@login_required
def profile(request):
    # If user came from the performers portal, use Uke4ia styling
    if request.META.get('HTTP_REFERER', '').startswith('/uke4ia'):
        template = "users/profile_uke4ia.html"
    else:
        template = "users/profile.html"

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("users:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, template, {
        "u_form": u_form,
        "p_form": p_form
    })
