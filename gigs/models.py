from django.db import models
from django.conf import settings  # CustomUser
from django.utils.timezone import now


class Venue(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='venues/', blank=True, null=True)

    def __str__(self):
        return self.name

class Gig(models.Model):
    venue = models.ForeignKey(Venue, related_name='gigs', on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()                      # The day of the performance
    start_time = models.TimeField()                # e.g., 19:30
    end_time = models.TimeField(null=True, blank=True)  # optional end time
    
    arrive_by = models.TimeField(null=True, blank=True) # optional early arrival

    #max_players = models.PositiveIntegerField(default=20)
    attire = models.CharField(max_length=255,null=True, blank=True)
    chairs = models.CharField(max_length=255,null=True, blank=True)
    arrive_by = models.TimeField(null=True, blank=True)
    # Hardcode site since it's only for StrumSphere
    site_name = models.CharField(max_length=20, default='strumsphere', editable=False)

    def __str__(self):
        return f"{self.title} at {self.venue.name}"





class Availability(models.Model):
    YES = 'Y'
    NO = 'N'
    MAYBE = 'M'
    AVAILABILITY_CHOICES = [
        (YES, 'Yes'),
        (NO, 'No'),
        (MAYBE, 'Maybe'),
    ]

    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=AVAILABILITY_CHOICES, default=MAYBE)

    class Meta:
        unique_together = ('gig', 'player')

    def __str__(self):
        return f"{self.player.username} -> {self.gig.title} ({self.get_status_display()})"
