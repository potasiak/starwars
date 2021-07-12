# Generated by Django 3.2.5 on 2021-07-12 10:05

from django.db import migrations, models
import django.utils.timezone
import starwars.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('file', models.FileField(upload_to=starwars.models.dataset_destination)),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
    ]
