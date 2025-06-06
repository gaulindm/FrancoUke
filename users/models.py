from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        UserPreference.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_preference(sender, instance, **kwargs):
    instance.userpreference.save()

class Profile(models.Model):
        #user = models.OntonOneField(User, on_delete=models.CASCADE)
        # Opted to not have pics on FrancoUKe but keeping Profile class for future implementation of bio
        # part 8: https://www.youtube.com/watch?v=FdVuKt_iuSI
        #image = models.ImageField(default='default.jpg',upload_to='profile_pics')

        def __str__(self):
                return f'{self.username} Profile'
        

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userpreference')
    transpose_value = models.IntegerField(default=0)  # e.g., semiton
    primary_instrument = models.CharField(
        max_length=20,
        choices=[
            ("guitar", "Guitar"),
            ("ukulele", "Ukulele"),
            ("baritone_ukulele", "Baritone Ukulele"),
            ("banjo", "Banjo"),
            ("mandolin", "Mandolin"),
        ],
        default="ukulele"
    )
    secondary_instrument = models.CharField(
        max_length=20,
        choices=[
            ("guitar", "Guitar"),
            ("ukulele", "Ukulele"),
            ("baritone_ukulele", "Baritone Ukulele"),
            ("banjo", "Banjo"),
            ("mandolin", "Mandolin"),
        ],
        default=None,  # No secondary instrument by default
        null=True,
        blank=True  # Allows the field to be optional
    )
    is_lefty = models.BooleanField(default=False)
    is_printing_alternate_chord = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.instrument} - Lefty: {self.is_lefty}, Alt Chords: {self.is_printing_alternate_chord}"