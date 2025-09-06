# serializers.py
from rest_framework import serializers
from .models import BoardItem, BoardItemPhoto, Event, EventPhoto
#from .models import PerformanceDetails


class EventPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = ["id", "image", "is_cover", "uploaded_at"]

'''
class PerformanceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceDetails
        fields = ["id", "attire", "chairs", "arrive_by"]
'''
        

class EventSerializer(serializers.ModelSerializer):
    photos = EventPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "board_item",
            "title",
            "description",
            "event_type",
            "status",
            "event_date",
            "start_time",
            "end_time",
            "location",
            "created_at",
            "updated_at",
            "photos",
        ]


"""
class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = "__all__"
        """


class BoardItemPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardItemPhoto
        fields = ["id", "image", "is_cover", "uploaded_at"]

class BoardItemSerializer(serializers.ModelSerializer):
    photos = BoardItemPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = BoardItem
        fields = [
            "id",
            "title",
            "description",
            "youtube_url",
            "youtube_embed_url",
            "media_file",
            "link",
            "event_date",
            "start_time",
            "end_time",
            "attire",
            "chairs",
            "arrive_by",
            "performance_type",
            "created_at",
            "position",
            "location",
            "rich_description",
            "is_rehearsal",
            "photos",
        ]