# board/migrations/0015_auto_clean_performance_and_add_is_public.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0014_boardcolumn_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='boarditem',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Performance',
        ),
        migrations.DeleteModel(
            name='PerformanceAvailability',
        ),
        migrations.DeleteModel(
            name='PerformanceDetails',
        ),
    ]
