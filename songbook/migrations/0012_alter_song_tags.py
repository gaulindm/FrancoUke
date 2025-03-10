# Generated by Django 5.1.2 on 2024-12-18 12:49

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('songbook', '0011_song_tags_delete_chord_delete_instrument'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
