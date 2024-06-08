from django.db import models

class TeamInformation(models.Model):
    league_id = models.IntegerField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    team = models.JSONField(blank=True, null=True)
    venue = models.JSONField(max_length=100, blank=True, null=True)

class TeamStatistics(models.Model):
    team = models.JSONField(max_length=100, blank=True, null=True)
    league = models.JSONField(blank=True, null=True)
    form = models.CharField(max_length=200, blank=True, null=True)
    fixtures = models.JSONField(blank=True, null=True)
    goals = models.JSONField(max_length=100, blank=True, null=True)
    biggest = models.JSONField(max_length=100, blank=True, null=True)
    clean_sheet = models.JSONField(blank=True, null=True)
    failed_to_score = models.JSONField(max_length=100, blank=True, null=True)
    penalty = models.JSONField(max_length=100, blank=True, null=True)
    lineups = models.JSONField(max_length=100, blank=True, null=True)
    cards = models.JSONField(max_length=100, blank=True, null=True)


class PlayersInformation(models.Model):
    team_id=models.ForeignKey(TeamInformation, on_delete=models.CASCADE)
    season = models.IntegerField(blank=True, null=True)
    player = models.JSONField(blank=True, null=True)
    statistics = models.JSONField(max_length=100, blank=True, null=True)