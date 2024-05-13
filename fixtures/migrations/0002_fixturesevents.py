# Generated by Django 5.0.4 on 2024-05-13 09:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixturesEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(max_length=100)),
                ('team_id', models.IntegerField()),
                ('team_name', models.CharField(max_length=100)),
                ('logo', models.URLField()),
                ('player_id', models.IntegerField()),
                ('player_name', models.CharField(max_length=100)),
                ('fixture_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.fixtures')),
            ],
        ),
    ]