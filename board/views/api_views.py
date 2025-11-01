# board/views/api_views.py
from rest_framework import viewsets
from ..models import BoardItem, Event
from ..serializers import BoardItemSerializer, EventSerializer

class BoardItemViewSet(viewsets.ModelViewSet):
    queryset = BoardItem.objects.all().order_by("-created_at")
    serializer_class = BoardItemSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = (
        Event.objects
        .select_related("board_item")
        .prefetch_related("photos")
        .order_by("event_date", "start_time", "title")
    )
    serializer_class = EventSerializer
