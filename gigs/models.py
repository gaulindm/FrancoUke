from django.db import models
from django.conf import settings  # CustomUser

class Gig(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_players = models.PositiveIntegerField(default=20)

    # Hardcode site since it's only for StrumSphere
    site_name = models.CharField(max_length=20, default='strumsphere', editable=False)

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%b %d, %Y')})"


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
