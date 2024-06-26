# Generated by Django 5.0.4 on 2024-06-08 14:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fixtures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league_id', models.IntegerField()),
                ('league_name', models.CharField(max_length=100)),
                ('league_country', models.CharField(max_length=100, null=True)),
                ('league_logo', models.URLField(max_length=250, null=True)),
                ('league_flag', models.URLField(max_length=250, null=True)),
                ('league_season', models.IntegerField()),
                ('league_round', models.CharField(max_length=100)),
                ('fixture_id', models.IntegerField()),
                ('fixture_timestamp', models.IntegerField()),
                ('fixture_referee', models.CharField(blank=True, max_length=250, null=True)),
                ('fixture_venue_name', models.CharField(blank=True, max_length=250, null=True)),
                ('fixture_venue_city', models.CharField(blank=True, max_length=250, null=True)),
                ('fixture_status_long', models.CharField(blank=True, max_length=250, null=True)),
                ('fixture_status_short', models.CharField(blank=True, max_length=250, null=True)),
                ('teams_home_name', models.CharField(blank=True, max_length=250, null=True)),
                ('teams_home_id', models.CharField(blank=True, max_length=250, null=True)),
                ('teams_home_logo', models.URLField(blank=True, max_length=250, null=True)),
                ('teams_home_winner', models.CharField(blank=True, max_length=250, null=True)),
                ('teams_away_name', models.CharField(blank=True, max_length=250, null=True)),
                ('teams_away_id', models.CharField(blank=True, max_length=250, null=True)),
                ('teams_away_logo', models.URLField(blank=True, max_length=250, null=True)),
                ('teams_away_winner', models.CharField(blank=True, max_length=250, null=True)),
                ('goals', models.CharField(blank=True, max_length=250, null=True)),
                ('score_halftime', models.CharField(blank=True, max_length=250, null=True)),
                ('score_fulltime', models.CharField(blank=True, max_length=250, null=True)),
                ('score_extratime', models.CharField(blank=True, max_length=250, null=True)),
                ('score_penalty', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FixturesEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(blank=True, max_length=100, null=True)),
                ('team_id', models.IntegerField(blank=True, null=True)),
                ('team_name', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.URLField(blank=True, null=True)),
                ('player_id', models.IntegerField(blank=True, null=True)),
                ('player_name', models.CharField(blank=True, max_length=100, null=True)),
                ('assist_id', models.CharField(blank=True, max_length=100, null=True)),
                ('assist_name', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
                ('detail', models.CharField(blank=True, max_length=100, null=True)),
                ('comments', models.CharField(blank=True, max_length=100, null=True)),
                ('fixture_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.fixtures')),
            ],
        ),
        migrations.CreateModel(
            name='FixturesLineUps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.IntegerField(blank=True, null=True)),
                ('team_name', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.URLField(blank=True, null=True)),
                ('team_color', models.JSONField(blank=True, null=True)),
                ('coach_id', models.IntegerField(blank=True, null=True)),
                ('coach_name', models.CharField(blank=True, max_length=100, null=True)),
                ('coach_photo', models.URLField(blank=True, null=True)),
                ('formation', models.CharField(blank=True, max_length=100, null=True)),
                ('startXI', models.JSONField(blank=True, null=True)),
                ('substitutes', models.JSONField(blank=True, max_length=100, null=True)),
                ('fixture_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.fixtures')),
            ],
        ),
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
                ('player_statistics', models.JSONField(blank=True, null=True)),
                ('fixture_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.fixtures')),
            ],
        ),
        migrations.CreateModel(
            name='FixtureStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statistics_data', models.JSONField(blank=True, null=True)),
                ('fixture_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fixtures.fixtures')),
            ],
        ),
    ]
