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


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = self.request.GET.get('site', 'FrancoUke')  # ✅ Ensure the correct site name
        return context



def register(request):
    site_name = request.GET.get("site", "FrancoUke")  # Default to FrancoUke

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')

            messages.success(
                request,
                f'Account created for {username}! Visit your <a href="{reverse("users:user_preferences")}?site={site_name}">Preferences</a> page to set up your instrument choices.'
            )

            return redirect(f'/users/login/?site={site_name}')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form, 'site_name': site_name})


@login_required
def user_preferences_view(request):
    """Allow users to set their instrument preferences, preserving site_name."""
    site_name = request.GET.get("site", "FrancoUke")  # Default to FrancoUke

    user_pref, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserPreferenceForm(request.POST, instance=user_pref)
        if form.is_valid():
            form.save()
            return render(request, "partials/close_modal.html")  # ✅ Close modal after saving
    else:
        form = UserPreferenceForm(instance=user_pref)

    return render(request, "partials/user_preferences_modal.html", {"form": form, "site_name": site_name})
