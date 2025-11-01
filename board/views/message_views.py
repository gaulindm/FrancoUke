# board/views/message_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ..models import BoardColumn, BoardMessage
from ..forms import BoardMessageForm
from ..decorators import group_required


@login_required
@group_required("Leaders")
def create_board_message(request, column_id):
    column = get_object_or_404(BoardColumn, pk=column_id)

    if request.method == "POST":
        form = BoardMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.column = column
            message.author = request.user
            message.save()
            return redirect("board:full_board")
    else:
        form = BoardMessageForm()

    return render(request, "board/message_form.html", {"form": form, "column": column})
