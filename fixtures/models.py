from django.db import models

class Fixtures(models.Model):
    league_id = models.IntegerField()
    league_name = models.CharField(max_length=100)
    league_country = models.CharField(max_length=100, null=True)
    league_logo = models.URLField(max_length=250, null=True)
    league_flag = models.URLField(max_length=250, null=True)
    league_season = models.IntegerField()
    league_round = models.CharField(max_length=100)
    fixture_id = models.IntegerField()
    fixture_timestamp = models.IntegerField()
    fixture_referee = models.CharField(max_length=250, blank=True, null=True)
    fixture_venue_name = models.CharField(max_length=250, blank=True, null=True)
    fixture_venue_city = models.CharField(max_length=250, blank=True, null=True)
    fixture_status_long = models.CharField(max_length=250, blank=True, null=True)
    fixture_status_short = models.CharField(max_length=250, blank=True, null=True)
    teams_home_name = models.CharField(max_length=250, blank=True, null=True)
    teams_home_id = models.CharField(max_length=250, blank=True, null=True)
    teams_home_logo = models.URLField(max_length=250, blank=True, null=True)
    teams_home_winner = models.CharField(max_length=250, blank=True, null=True)
    teams_away_name = models.CharField(max_length=250, blank=True, null=True)
    teams_away_id = models.CharField(max_length=250, blank=True, null=True)
    teams_away_logo = models.URLField(max_length=250, blank=True, null=True)
    teams_away_winner = models.CharField(max_length=250, blank=True, null=True)
    goals = models.CharField(max_length=250, blank=True, null=True)
    score_halftime = models.CharField(max_length=250, blank=True, null=True)
    score_fulltime = models.CharField(max_length=250, blank=True, null=True)
    score_extratime = models.CharField(max_length=250, blank=True, null=True)
    score_penalty = models.CharField(max_length=250, blank=True, null=True)


class FixtureStats(models.Model):
    fixture_id = models.ForeignKey(Fixtures, on_delete=models.CASCADE)
    statistics_data = models.JSONField(blank=True, null=True)
    


class FixturesEvents(models.Model):
    fixture_id = models.ForeignKey(Fixtures, on_delete=models.CASCADE)
    time = models.CharField(max_length=100, blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.CharField(max_length=100, blank=True, null=True)
    assist_id = models.CharField(max_length=100, blank=True, null=True)
    assist_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    detail = models.CharField(max_length=100, blank=True, null=True)
    comments = models.CharField(max_length=100, blank=True, null=True)


class FixturesLineUps(models.Model):
    fixture_id = models.ForeignKey(Fixtures, on_delete=models.CASCADE)
    team_id = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    team_color = models.JSONField(blank=True, null=True)
    coach_id = models.IntegerField(blank=True, null=True)
    coach_name = models.CharField(max_length=100, blank=True, null=True)
    coach_photo = models.URLField(blank=True, null=True)
    formation = models.CharField(max_length=100, blank=True, null=True)
    startXI = models.JSONField(blank=True, null=True)
    substitutes = models.JSONField(max_length=100, blank=True, null=True)



class FixturesPlayerStats(models.Model):
    fixture_id = models.ForeignKey(Fixtures, on_delete=models.CASCADE)
    team_id = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    update = models.CharField(max_length=100, blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
    player_name = models.CharField(max_length=100, blank=True, null=True)
    player_photo = models.URLField(blank=True, null=True)
    player_statistics = models.JSONField(blank=True, null=True)
