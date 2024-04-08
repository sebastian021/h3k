from django.db import models

class Fixtures(models.Model):
    league_id = models.IntegerField()
    league_name = models.CharField(max_length=100)
    league_season = models.IntegerField()
    league_round = models.CharField(max_length=100)
    fixture_id = models.IntegerField()
    fixture_timestamp = models.IntegerField()
    