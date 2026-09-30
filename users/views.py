# users/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomUserCreationForm, UserPreferenceForm
from .models import UserPreference


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = self.request.GET.get("site", "FrancoUke")
        return context


def register(request):
    site_name = request.GET.get("site", "FrancoUke")  # Default to FrancoUke

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
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
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form, "site_name": site_name})


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

    # HTMX request -> modal partial
    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "partials/user_preferences_modal.html",
            {"form": form, "site_name": site_name},
        )

    # Full-page request
    return render(
        request,
        "users/user_preference_form.html",
        {"form": form, "site_name": site_name},
    )


@login_required
def profile(request):
    template = "users/profile.html"

    # TODO: UserUpdateForm and ProfileUpdateForm are not imported anywhere in
    # this file (see the notes below). Fix or remove this view before relying on it.
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("users:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, template, {"u_form": u_form, "p_form": p_form})