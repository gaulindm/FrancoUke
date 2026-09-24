# core/group_access.py
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Group


def get_active_group_or_404(group_slug):
    """Resolve a Group by slug for public/unauthenticated views."""
    return get_object_or_404(Group, slug=group_slug, is_active=True)


def group_member_required(view_func):
    """
    Decorator for views mounted under /board/<group_slug>/...

    - Redirects anonymous users to login (preserving the target URL).
    - Raises PermissionDenied (403) if the logged-in user isn't a member
      of this specific group (superusers always pass).
    - Attaches the resolved Group as request.group for the view to use.
    """
    @wraps(view_func)
    def wrapper(request, group_slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=group_slug, is_active=True)

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        is_member = group.memberships.filter(user=request.user).exists()
        if not (request.user.is_superuser or is_member):
            raise PermissionDenied("You're not a member of this group.")

        request.group = group
        return view_func(request, group_slug, *args, **kwargs)

    return wrapper