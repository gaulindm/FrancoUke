from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create or update the Song Taggers group."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(
            name="Song Taggers"
        )

        permissions = Permission.objects.filter(
            content_type__app_label="songbook",
            content_type__model="song",
            codename__in=[
                "view_song",
                "change_song",
            ],
        )

        group.permissions.set(permissions)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Created 'Song Taggers' group."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Updated 'Song Taggers' group."
                )
            )

        self.stdout.write(
            "Permissions assigned:"
        )

        for permission in permissions:
            self.stdout.write(
                f"  - {permission.codename}"
            )