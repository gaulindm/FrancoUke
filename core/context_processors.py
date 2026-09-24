# core/context_processors.py
def user_groups(request):
    """
    Makes the current user's group memberships available in every template
    as `user_groups` (a list of Group objects).
    """
    if not request.user.is_authenticated:
        return {"user_groups": []}

    groups = [m.group for m in request.user.group_memberships.select_related("group")]
    return {"user_groups": groups}