# Generated by Django 5.1.2 on 2024-11-03 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songbook', '0007_song_lyrics_with_chords_alter_song_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='lyrics_with_chords',
            field=models.TextField(blank=True),
        ),
    ]
