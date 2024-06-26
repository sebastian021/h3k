# Generated by Django 5.0.4 on 2024-06-24 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('team_id', models.IntegerField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(blank=True, max_length=200, null=True)),
                ('team_logo', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_code', models.CharField(blank=True, max_length=50, null=True)),
                ('team_country', models.CharField(blank=True, max_length=150, null=True)),
                ('team_founded', models.IntegerField(blank=True, null=True)),
                ('team_national', models.BooleanField(blank=True, null=True)),
                ('venue', models.JSONField(blank=True, max_length=100, null=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.teams')),
            ],
        ),
        migrations.CreateModel(
            name='PlayersInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.IntegerField(blank=True, null=True)),
                ('player', models.JSONField(blank=True, null=True)),
                ('statistics', models.JSONField(blank=True, max_length=100, null=True)),
                ('team_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.teams')),
            ],
        ),
        migrations.CreateModel(
            name='TeamStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league_id', models.IntegerField(blank=True, null=True)),
                ('league_name', models.CharField(blank=True, max_length=200, null=True)),
                ('league_country', models.CharField(blank=True, max_length=200, null=True)),
                ('league_logo', models.URLField(blank=True, null=True)),
                ('league_flag', models.URLField(blank=True, null=True)),
                ('season', models.IntegerField(blank=True, null=True)),
                ('form', models.CharField(blank=True, max_length=100, null=True)),
                ('fixtures', models.JSONField(blank=True, null=True)),
                ('goals', models.JSONField(blank=True, max_length=100, null=True)),
                ('biggest', models.JSONField(blank=True, max_length=100, null=True)),
                ('clean_sheet', models.JSONField(blank=True, null=True)),
                ('failed_to_score', models.JSONField(blank=True, max_length=100, null=True)),
                ('penalty', models.JSONField(blank=True, max_length=100, null=True)),
                ('lineups', models.JSONField(blank=True, max_length=100, null=True)),
                ('cards', models.JSONField(blank=True, max_length=100, null=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.teams')),
            ],
        ),
    ]
