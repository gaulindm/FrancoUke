import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction, IntegrityError


class Command(BaseCommand):
    help = "Import users from a CSV file and add them to the performers group"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        User = get_user_model()

        # Ensure the performers group exists
        performers_group, created = Group.objects.get_or_create(name="performers")
        if created:
            self.stdout.write(self.style.SUCCESS("Created 'performers' group."))

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

            for row in reader:
                username = row["username"].strip()
                firstname = row["firstname"].strip()
                lastname = row["lastname"].strip()
                email = row["email"].strip()
                password = row["password"].strip()

                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(
                        f"User {username} already exists, skipping..."
                    ))
                    continue

                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.WARNING(
                        f"Email {email} already exists, skipping..."
                    ))
                    continue

                try:
                    user = User.objects.create_user(
                        username=username,
                        first_name=firstname,
                        last_name=lastname,
                        email=email,
                        password=password
                    )
                except IntegrityError as e:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to create {username}: {e}"
                    ))
                    continue

                user.groups.add(performers_group)
                self.stdout.write(self.style.SUCCESS(f"Created user {username} ✅"))
