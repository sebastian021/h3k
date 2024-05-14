# Generated by Django 5.0.4 on 2024-05-14 11:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0002_fixtureslineups'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixturesPlayerStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.IntegerField(blank=True, null=True)),
                ('team_name', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.URLField(blank=True, null=True)),
                ('update', models.CharField(blank=True, max_length=100, null=True)),
                ('player_id', models.IntegerField(blank=True, null=True)),
                ('player_name', models.CharField(blank=True, max_length=100, null=True)),
                ('player_photo', models.URLField(blank=True, null=True)),
                ('player_statistics', models.CharField(blank=True, max_length=100, null=True)),
                ('fixture_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.fixtures')),
            ],
        ),
    ]
