from django.db import models

# Create your models here.
from django.db import models

class Match(models.Model):
    fixture_id = models.IntegerField(null=True)
    match_date = models.DateTimeField(null=True)
    match_timestamp = models.IntegerField(null=True)
    match_periods_first = models.CharField(max_length=250, null=True)
    match_periods_second = models.CharField(max_length=250, null=True)
    match_venue_name = models.CharField(max_length=250, null=True)
    match_venue_city = models.CharField(max_length=250, null=True)
    match_status_long = models.CharField(max_length=250, null=True)
    league_id = models.CharField(max_length=250, null=True)
    league_name = models.CharField(max_length=100, null=True)
    league_country = models.CharField(max_length=250, null=True)
    league_logo = models.URLField(max_length=250, null=True)
    league_flag = models.URLField(max_length=250, null=True)
    league_season = models.IntegerField(null=True)
    league_round = models.CharField(max_length=100, null=True)
    home_team_name = models.CharField(max_length=250, null=True)
    home_team_logo = models.URLField(max_length=250, null=True)
    home_team_winner = models.CharField(max_length=250, null=True)
    away_team_name = models.CharField(max_length=250, null=True)
    away_team_logo = models.URLField(max_length=250, null=True)
    away_team_winner = models.CharField(max_length=250, null=True)
    home_team_goals = models.IntegerField(null=True)
    away_team_goals = models.IntegerField(null=True)
    halftime_score = models.CharField(max_length=250, null=True)
    fulltime_score = models.CharField(max_length=250, null=True)
    extratime_score = models.CharField(max_length=250, null=True)
    penalty_score = models.CharField(max_length=250, null=True)
    match_refree = models.CharField(max_length=250, blank=True, null=True)

class MatchStats(models.Model):
    fixture_id = models.ForeignKey(Match, blank=True, null=True, on_delete=models.CASCADE)
    statistics_data = models.JSONField(blank=True, null=True)
    
