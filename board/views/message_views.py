# board/views/message_views.py
from django.shortcuts import render, get_object_or_404, redirect

from ..models import BoardColumn, BoardMessage
from ..forms import BoardMessageForm
from ..decorators import group_required
from core.group_access import group_member_required


@group_member_required
@group_required("Leaders")
def create_board_message(request, group_slug, column_id):
    group = request.group
    column = get_object_or_404(BoardColumn, pk=column_id, group=group)

    if request.method == "POST":
        form = BoardMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.column = column
            message.author = request.user
            message.save()
            return redirect("board:full_board", group_slug=group_slug)
    else:
        form = BoardMessageForm()

    return render(request, "board/message_form.html", {"form": form, "column": column, "group": group})