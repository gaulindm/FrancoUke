from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from urllib.parse import urlparse, parse_qs


# -------------------------
# Board + Items
# -------------------------
class BoardColumn(models.Model):
    COLUMN_TYPES = [
        ("general", "General"),
        ("photos", "Photo Gallery"),
        ("venue", "Venue"),
        ("songs_to_listen", "Songs To Listen"),
        # 🚀 rehearsals/past performances now handled by Performance
    ]

    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    column_type = models.CharField(max_length=20, choices=COLUMN_TYPES, default="general")
    # 🔑 Optional link to Venue if this is a venue-column
    venue = models.ForeignKey("Venue", on_delete=models.CASCADE, null=True, blank=True, related_name="board_column")



    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to="venues/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # ✅ ordering like BoardColumn
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "name"]

    def __str__(self):
        return self.name


class BoardItem(models.Model):
    column = models.ForeignKey("BoardColumn", on_delete=models.CASCADE, null=True, blank=True, related_name="items")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, null=True, blank=True, related_name="board_items")

    # Fields for non-event cards
    title = models.CharField(max_length=255, blank=True)
    rich_description = RichTextField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    media_file = models.FileField(upload_to="board_media/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        if self.event:
            return f"Event: {self.event.title}"
        return self.title or "Board Item"

    @property
    def youtube_embed_url(self):
        """Return proper YouTube embed link if possible."""
        if not self.youtube_url:
            return None

        parsed = urlparse(self.youtube_url)
        query = parse_qs(parsed.query)
        video_id = None
        start_time = None

        # Handle normal YouTube links: https://www.youtube.com/watch?v=abc123
        if "youtube.com" in parsed.netloc:
            if "v" in query:
                video_id = query["v"][0]
            elif parsed.path.startswith("/embed/"):
                video_id = parsed.path.split("/")[-1]
            elif parsed.path.startswith("/shorts/"):
                video_id = parsed.path.split("/")[-1]

            if "t" in query:
                start_time = query["t"][0].replace("s", "")

        # Handle shortened links: https://youtu.be/abc123?t=90
        elif "youtu.be" in parsed.netloc:
            video_id = parsed.path.strip("/")
            if "t" in query:
                start_time = query["t"][0].replace("s", "")

        if not video_id:
            return None

        embed_url = f"https://www.youtube.com/embed/{video_id}"
        if start_time:
            embed_url += f"?start={start_time}"
        return embed_url



# -------------------------
# Performances + Availability
# -------------------------
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
    venue = models.ForeignKey(
            "Venue",
            on_delete=models.SET_NULL,
            related_name="performances",
            null=True,
            blank=True
        )
    location = models.CharField(max_length=255, blank=True)
    attire = models.CharField(max_length=255, null=True, blank=True)
    chairs = models.CharField(max_length=255, null=True, blank=True)

    performance_type = models.CharField(max_length=20, choices=PERFORMANCE_CHOICES, default="upcoming")
    is_rehearsal = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_my_availability_display(self):
        if hasattr(self, "my_availability") and self.my_availability:
            mapping = {"yes": "Yes", "no": "No", "maybe": "Maybe"}
            return mapping.get(self.my_availability, self.my_availability)
        return "Not set"

    def __str__(self):
        return f"{self.board_item.title} ({self.get_performance_type_display()})"


class PerformanceAvailability(models.Model):
    YES = "yes"
    NO = "no"
    MAYBE = "maybe"

    STATUS_CHOICES = [
        (YES, "Yes"),
        (NO, "No"),
        (MAYBE, "Maybe"),
    ]

    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="performance_availabilities"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=MAYBE)

    class Meta:
        unique_together = ("performance", "user")

    def __str__(self):
        return f"{self.user} – {self.performance.board_item.title} – {self.get_status_display()}"


class BoardItemPhoto(models.Model):
    board_item = models.ForeignKey(BoardItem, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="board_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"Photo for {self.board_item.title}"


# -------------------------
# Events
# -------------------------
from django.db import models
from ckeditor.fields import RichTextField

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

    # 🔑 Optional Venue link (for recurring venue-based events)
    venue = models.ForeignKey(
        "Venue",
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True
    )

    # 🔑 Optional BoardColumn link (for "Upcoming", "Past", "To Be Confirmed")
    column = models.ForeignKey(
        "BoardColumn",
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255)
    rich_description = RichTextField(blank=True)  
    rich_notes = RichTextField(blank=True)       

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        default="performance"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="upcoming"
    )

    event_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    
    
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #last added fields
    arrive_by = models.TimeField(null=True, blank=True) # optional early arrival
    attire = models.CharField(max_length=255,null=True, blank=True)
    chairs = models.CharField(max_length=255,null=True, blank=True)
 

    class Meta:
        ordering = ["event_date", "start_time", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()} - {self.get_status_display()})"

    @property
    def cover_photo(self):
        return self.photos.filter(is_cover=True).first() or self.photos.first()



class PerformanceDetails(models.Model):
    """Extra fields only for performances."""
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="performance_details")
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

# -------------------------
# Event Availabilty
# -------------------------

from django.conf import settings

class EventAvailability(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="availabilities")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("unavailable", "Unavailable"),
            ("maybe", "Maybe"),
        ],
    )
