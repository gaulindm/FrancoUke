# board/decorators.py
from django.core.exceptions import PermissionDenied

def group_required(group_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied  # 403 Forbidden
        return _wrapped_view
    return decorator
