from django.db import migrations


def seed_groups(apps, schema_editor):
    Group = apps.get_model("core", "Group")
    Group.objects.get_or_create(
        slug="i-ukes",
        defaults={"name": "I-Ukes", "contact_email": ""},
    )
    Group.objects.get_or_create(
        slug="friendly-wood-chuckers",
        defaults={"name": "Friendly Wood Chuckers", "contact_email": ""},
    )


def unseed_groups(apps, schema_editor):
    Group = apps.get_model("core", "Group")
    Group.objects.filter(slug__in=["i-ukes", "friendly-wood-chuckers"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_groups, unseed_groups),
    ]