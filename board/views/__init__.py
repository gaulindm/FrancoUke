"""
Public view exports for easy imports in urls.py etc.
This module re-exports the main view callables from the split modules.
"""

from .board_views import (
    full_board_view,
    performer_event_list,
    availability_matrix,
    board_item_gallery_view,
    item_photo_list,
)

from .event_views import (
    event_detail,
    update_event_availability,
    rehearsal_detail_view,
    set_availability,
)

from .message_views import create_board_message
from .api_views import BoardItemViewSet, EventViewSet

# ✅ Add the new rehearsal view imports
from .rehearsal_views import (
    edit_rehearsal_details,
    edit_song_rehearsal_notes,
)

__all__ = [
    "full_board_view",
    "performer_event_list",
    "availability_matrix",
    "board_item_gallery_view",
    "item_photo_list",
    "event_detail",
    "update_event_availability",
    "rehearsal_detail_view",
    "set_availability",
    "create_board_message",
    "BoardItemViewSet",
    "EventViewSet",
    "edit_rehearsal_details",
    "edit_song_rehearsal_notes",
]
