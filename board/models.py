from django.db import models
from urllib.parse import urlparse, parse_qs
from ckeditor.fields import RichTextField


class BoardColumn(models.Model):
    COLUMN_TYPES = [
        ('general', 'General'),
        ('photos', 'Photo Gallery'),
        ('venue', 'Venue'),
        ('songs to listen', 'Songs To Listen'),
        ('rehearsal','Rehearsal'),
        ('rehearsal notes','Rehearsal Notes'),
        ('past_performances', 'Past Performances'),  # ✅ New type

        # Add more if needed
    ]

    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    column_type = models.CharField(
        max_length=20,
        choices=COLUMN_TYPES,
        default='general'
    )

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name




class BoardItem(models.Model):
    column = models.ForeignKey(BoardColumn, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(blank=True, null=True)  # Optional: Embed a video
    media_file = models.FileField(upload_to='board_media/', blank=True, null=True)  # Optional audio/video
    link = models.URLField(blank=True, null=True)  # Optional external link
    
    event_date = models.DateField(blank=True, null=True)       # 📅 Date only
    start_time = models.TimeField(blank=True, null=True)       # 🕑 Start
    end_time = models.TimeField(blank=True, null=True)         # 🕒 End

    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0)  # Position in column
    location = models.CharField(max_length=255, blank=True)  # ✅ Address
    rich_description = RichTextField(blank=True, null=True)   # ✅ Email body with formatting
    is_rehearsal = models.BooleanField(default=False)          # ✅ Tag this as a rehearsal

    def __str__(self):
        return self.title

    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return None

        # Convert to embeddable URL
        parsed = urlparse(self.youtube_url)
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]

        start_time = query.get("t", [None])[0]

        if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            if start_time:
                embed_url += f"?start={start_time.replace('s', '')}"
            return embed_url

        # handle youtu.be links
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.strip("/")
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            if parsed.query:
                if "t=" in parsed.query:
                    start_time = parsed.query.split("t=")[-1]
                    embed_url += f"?start={start_time.replace('s', '')}"
            return embed_url
        return None



   
    @property
    def cover_photo(self):
        return self.photos.filter(is_cover=True).first() or self.photos.first()



class BoardItemPhoto(models.Model):
    board_item = models.ForeignKey('BoardItem', on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='board_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_cover = models.BooleanField(default=False)  # ✅ New field

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
    rehearsal = models.ForeignKey('BoardItem', on_delete=models.CASCADE, related_name='availabilities')
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'rehearsal')

    def __str__(self):
        return f"{self.user} → {self.get_status_display()} for {self.rehearsal.title}"
