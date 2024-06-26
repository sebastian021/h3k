from django.db import models

class Leagues(models.Model):
    league_id = models.IntegerField(primary_key=True)
    league_name = models.CharField(max_length=500, blank=True, null=True)  # Increased to 500
    league_enName = models.CharField(max_length=500, blank=True, null=True)  # Increased to 500
    league_faName = models.CharField(max_length=500, blank=True, null=True)  # Increased to 500
    league_type = models.CharField(max_length=50, blank=True, null=True)
    league_logo = models.URLField(blank=True, null=True)
    league_country = models.JSONField()
    seasons = models.JSONField(blank=True, null=True)  # Increased to 500
    num_teams = models.IntegerField(blank=True, null=True)
    num_rounds = models.IntegerField(blank=True, null=True)
     
