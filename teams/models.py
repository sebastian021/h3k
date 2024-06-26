from django.db import models


class Teams(models.Model):
    team_id = models.IntegerField(primary_key=True)
    team_name = models.CharField(max_length=200, blank=True, null=True)
    team_logo = models.URLField(blank=True, null=True)

class TeamInformation(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    team_code = models.CharField(max_length=50, blank=True, null=True)
    team_country = models.CharField(max_length=150, blank=True, null=True)
    team_founded = models.IntegerField(blank=True, null=True)
    team_national = models.BooleanField(blank=True, null=True)
    venue = models.JSONField(max_length=100, blank=True, null=True)

class TeamStatistics(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    league_id = models.IntegerField(blank=True, null=True)
    league_name = models.CharField(max_length=200, blank=True, null=True)
    league_country = models.CharField(max_length=200, blank=True, null=True)
    league_logo = models.URLField(blank=True, null=True)
    league_flag = models.URLField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    form = models.CharField(max_length=100, blank=True, null=True)
    fixtures = models.JSONField(blank=True, null=True)
    goals = models.JSONField(max_length=100, blank=True, null=True)
    biggest = models.JSONField(max_length=100, blank=True, null=True)
    clean_sheet = models.JSONField(blank=True, null=True)
    failed_to_score = models.JSONField(max_length=100, blank=True, null=True)
    penalty = models.JSONField(max_length=100, blank=True, null=True)
    lineups = models.JSONField(max_length=100, blank=True, null=True)
    cards = models.JSONField(max_length=100, blank=True, null=True)


class PlayersInformation(models.Model):
    team=models.ForeignKey(Teams, on_delete=models.CASCADE)
    season = models.IntegerField(blank=True, null=True)
    player = models.JSONField(blank=True, null=True)
    statistics = models.JSONField(max_length=100, blank=True, null=True)