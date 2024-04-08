from django.db import models

class Standing(models.Model):
    league_id = models.IntegerField(blank=True, null=True)
    league_name = models.CharField(max_length=100, blank=True, null=True)
    league_country = models.TextField(max_length=100, blank=True, null=True)
    league_logo = models.URLField(max_length=200, blank=True, null=True)
    league_flag = models.URLField(max_length=200, blank=True, null=True)
    league_season = models.IntegerField(blank=True, null=True)
    standings_data = models.JSONField()
