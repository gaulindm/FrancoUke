from django.db import migrations, models
import django.conf
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')],
                    default='maybe',
                    max_length=10
                )),
                ('performance', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='availabilities',
                    to='board.performance'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='performance_availabilities',
                    to=django.conf.settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'unique_together': {('performance', 'user')},
            },
        ),
    ]
