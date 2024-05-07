# Generated by Django 5.0.4 on 2024-04-25 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixtures', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixtures',
            name='fixture_referee',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='fixture_status_long',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='fixture_status_short',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='fixture_venue_city',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='fixture_venue_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='goals',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='league_country',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='league_flag',
            field=models.URLField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='league_logo',
            field=models.URLField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='score_extratime',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='score_fulltime',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='score_halftime',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='score_penalty',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_away_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_away_logo',
            field=models.URLField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_away_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_away_winner',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_home_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_home_logo',
            field=models.URLField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_home_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='fixtures',
            name='teams_home_winner',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
