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
    - Attaches to the request:
        request.group           -> the resolved Group
        request.group_role      -> "leader" or "performer" (superusers count as "leader")
        request.is_group_leader -> True/False, handy in views and templates
    """
    @wraps(view_func)
    def wrapper(request, group_slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=group_slug, is_active=True)

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        membership = group.memberships.filter(user=request.user).first()

        if request.user.is_superuser:
            role = "leader"
        elif membership:
            role = membership.role
        else:
            raise PermissionDenied("You're not a member of this group.")

        request.group = group
        request.group_role = role
        request.is_group_leader = (role == "leader")
        return view_func(request, group_slug, *args, **kwargs)

    return wrapper


def group_leader_required(view_func):
    """
    Same as group_member_required, but the user must also be a leader
    of THIS group (superusers pass). Replaces the old site-wide
    auth.Group "Leaders" check on the board.
    """
    @wraps(view_func)
    @group_member_required
    def wrapper(request, group_slug, *args, **kwargs):
        if not request.is_group_leader:
            raise PermissionDenied("Only leaders of this group can do this.")
        return view_func(request, group_slug, *args, **kwargs)

    return wrapper