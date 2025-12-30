# Save as: cube/migrations/000X_add_category_field.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cube', '0004_alter_cubestate_roofpig_colored_and_more'),  # Replace with your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='cubestate',
            name='category',
            field=models.CharField(
                max_length=50,
                blank=True,
                help_text="Category/group for filtering (e.g., 'basic', 'corner-right-edge-right')"
            ),
        ),
        migrations.AddField(
            model_name='cubestate',
            name='difficulty',
            field=models.CharField(
                max_length=20,
                blank=True,
                choices=[
                    ('facile', 'Facile'),
                    ('moyen', 'Moyen'),
                    ('difficile', 'Difficile'),
                ],
                help_text="Difficulty level of the case"
            ),
        ),
    ]