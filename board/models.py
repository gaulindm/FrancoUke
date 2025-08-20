from django.db import models
from ckeditor.fields import RichTextField
from urllib.parse import urlparse, parse_qs

class BoardColumn(models.Model):
    COLUMN_TYPES = [
        ('general', 'General'),
        ('photos', 'Photo Gallery'),
        ('venue', 'Venue'),
        ('songs_to_listen', 'Songs To Listen'),
        # 🚀 removed rehearsals/past performances — handled by Performance
    ]

    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    column_type = models.CharField(max_length=20, choices=COLUMN_TYPES, default='general')

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name


class BoardItem(models.Model):
    column = models.ForeignKey(BoardColumn, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(blank=True, null=True)
    media_file = models.FileField(upload_to='board_media/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    rich_description = RichTextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return None
        parsed = urlparse(self.youtube_url)
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]
        start_time = query.get("t", [None])[0]
        if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            if start_time:
                embed_url += f"?start={start_time.replace('s', '')}"
            return embed_url
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.strip("/")
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            if parsed.query and "t=" in parsed.query:
                start_time = parsed.query.split("t=")[-1]
                embed_url += f"?start={start_time.replace('s', '')}"
            return embed_url
        return None

class Performance(models.Model):
    PERFORMANCE_CHOICES = [
        ("upcoming", "Upcoming"),
        ("tbc", "To Be Confirmed"),
        ("past", "Past Performance"),
    ]

    board_item = models.OneToOneField(BoardItem, on_delete=models.CASCADE, related_name="performance")

    event_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    arrive_by = models.TimeField(blank=True, null=True)

    location = models.CharField(max_length=255, blank=True)
    attire = models.CharField(max_length=255, null=True, blank=True)
    chairs = models.CharField(max_length=255, null=True, blank=True)

    performance_type = models.CharField(max_length=20, choices=PERFORMANCE_CHOICES, default="upcoming")
    is_rehearsal = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.board_item.title} ({self.get_performance_type_display()})"


class BoardItemPhoto(models.Model):
    board_item = models.ForeignKey(BoardItem, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='board_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"Photo for {self.board_item.title}"





    # board/models.py
from django.db import models
from django.conf import settings  # needed for referencing the user model


class RehearsalAvailability(models.Model):
    ATTENDANCE_CHOICES = [
        ('yes', "✅ I'm coming"),
        ('maybe', "❓ Not sure"),
        ('no', "❌ Can't make it"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    performance = models.ForeignKey(
        "Performance",
        on_delete=models.CASCADE,
        related_name="availabilities",
        null=True,
        blank=True
    )
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'performance')

    def __str__(self):
        return f"{self.user} → {self.get_status_display()} for {self.performance.board_item.title}"


class Event(models.Model):
    EVENT_TYPES = [
        ("rehearsal", "Rehearsal"),
        ("performance", "Performance"),
        ("general", "General Event"),
    ]

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("tbc", "To Be Confirmed"),
        ("past", "Past"),
    ]

    # Optional link to a board item (to show an event within a card/column)
    # Safe and nullable so it won't break existing data.
    board_item = models.ForeignKey(
        'BoardItem',
        on_delete=models.SET_NULL,
        related_name='events',
        null=True,
        blank=True
    )



    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="performance")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")

    event_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            ordering = ["event_date", "start_time", "title"]


    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()} - {self.get_status_display()})"

class PerformanceDetails(models.Model):
    """Extra fields only for performances (gigs)."""
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="performance_details"
    )
    attire = models.CharField(max_length=255, null=True, blank=True)
    chairs = models.CharField(max_length=255, null=True, blank=True)
    arrive_by = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Performance Details for {self.event.title}"


class RehearsalDetails(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="rehearsal_details")
    notes = models.TextField(blank=True, null=True)

class EventPhoto(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="event_photos/")
    is_cover = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.event.title}"

