from django.db import models
from django.utils.translation import gettext_lazy as _
    
class Leagues(models.Model):
    league_id = models.IntegerField(primary_key=True)
    league_name = models.CharField(max_length=500, blank=True, null=True) 
    league_enName = models.CharField(max_length=500, blank=True, null=True) 
    league_faName = models.CharField(max_length=500, blank=True, null=True) 
    league_type = models.CharField(max_length=50, blank=True, null=True)
    league_logo = models.URLField(blank=True, null=True)
    league_country = models.JSONField()
    league_country_flag = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.league_name
    

class Season(models.Model):
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE)
    year = models.IntegerField()
    start = models.DateField()
    end = models.DateField()



class LeagueTeams(models.Model):
    league_id = models.ForeignKey(Leagues, on_delete=models.CASCADE)
    season = models.ManyToManyField(Season)
    team_id = models.IntegerField(primary_key=True)
    team_name = models.CharField(max_length=500, blank=True, null=True)
    team_faName = models.CharField(max_length=500, blank=True, null=True)
    team_logo = models.URLField(blank=True, null=True)
    team_code = models.CharField(max_length=50, blank=True, null=True)
    team_country = models.CharField(max_length=500, blank=True, null=True)
    team_faCountry = models.CharField(max_length=500, blank=True, null=True)
    team_founded = models.IntegerField(blank=True, null=True)
    team_national = models.BooleanField(default=False)
    venue = models.JSONField()
    
    def __str__(self):
        return self.team_name
    


class Coach(models.Model):
    coach_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    faName= models.CharField(max_length=500, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=500, blank=True, null=True)
    birth_faPlace = models.CharField(max_length=500, blank=True, null=True)
    birth_country = models.CharField(max_length=500, blank=True, null=True)
    birth_faCountry = models.CharField(max_length=500, blank=True, null=True)
    nationality = models.CharField(max_length=500, blank=True, null=True)
    faNationality = models.CharField(max_length=500, blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    team = models.ForeignKey(LeagueTeams, on_delete=models.CASCADE)
    career = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name



class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    faName = models.CharField(max_length=500, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)
    birthPlace = models.CharField(max_length=500, blank=True, null=True)
    faBirthPlace = models.CharField(max_length=500, blank=True, null=True)
    birthCountry = models.CharField(max_length=500, blank=True, null=True)
    faBirthCountry = models.CharField(max_length=500, blank=True, null=True)
    nationality = models.CharField(max_length=500, blank=True, null=True)
    faNationality = models.CharField(max_length=500, blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    injured = models.BooleanField(default=False)
    photo = models.URLField(blank=True, null=True)
    appearences = models.IntegerField(blank=True, null=True)
    lineups = models.IntegerField(blank=True, null=True)
    minutes = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    grid = models.CharField(max_length=50, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    captain = models.BooleanField(default=False)
    substitutesIn = models.IntegerField(blank=True, null=True)
    substitutesOut = models.IntegerField(blank=True, null=True)
    bench = models.IntegerField(blank=True, null=True)
    shotsTotal = models.IntegerField(blank=True, null=True)
    shotsOn = models.IntegerField(blank=True, null=True)
    goalsTotal = models.IntegerField(blank=True, null=True)
    goalsConceded = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    passTotal = models.IntegerField(blank=True, null=True)
    passKey = models.IntegerField(blank=True, null=True)
    passAccuracy = models.FloatField(blank=True, null=True)
    tacklesTotal = models.IntegerField(blank=True, null=True)
    blocks = models.IntegerField(blank=True, null=True)
    interceptions = models.IntegerField(blank=True, null=True)
    duelsTotal = models.IntegerField(blank=True, null=True)
    duelsWon = models.IntegerField(blank=True, null=True)
    dribbleAttempts = models.IntegerField(blank=True, null=True)
    dribbleSuccess = models.IntegerField(blank=True, null=True)
    dribblePast = models.IntegerField(blank=True, null=True)
    foulsDrawn = models.IntegerField(blank=True, null=True)
    foulsCommitted = models.IntegerField(blank=True, null=True)
    cardsYellow = models.IntegerField(blank=True, null=True)
    cardsYellowRed = models.IntegerField(blank=True, null=True)
    cardsRed = models.IntegerField(blank=True, null=True)
    penaltyWon = models.IntegerField(blank=True, null=True)
    penaltyCommited = models.IntegerField(blank=True, null=True)
    penaltyScored = models.IntegerField(blank=True, null=True)
    penaltyMissed = models.IntegerField(blank=True, null=True)
    penaltySaved = models.IntegerField(blank=True, null=True)
    team = models.ForeignKey(LeagueTeams, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Fixture(models.Model):
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='fixtures')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='fixtures')
    fixture_id = models.IntegerField(primary_key=True, unique=True)
    fixture_referee = models.CharField(max_length=250, blank=True, null=True)
    fixture_timestamp = models.IntegerField()
    fixture_periods_first = models.IntegerField(null=True)
    fixture_periods_second = models.IntegerField(null=True)
    fixture_venue_name = models.CharField(max_length=250, blank=True, null=True)
    fixture_venue_faName = models.CharField(max_length=250, blank=True, null=True)
    fixture_venue_city = models.CharField(max_length=250, blank=True, null=True)
    fixture_venue_faCity = models.CharField(max_length=250, blank=True, null=True)
    fixture_status_long = models.CharField(max_length=250, blank=True, null=True)
    fixture_status_short = models.CharField(max_length=250, blank=True, null=True)
    fixture_status_elapsed = models.CharField(max_length=250, blank=True, null=True)
    league_round = models.CharField(max_length=100)
    teams_home = models.ForeignKey(LeagueTeams, blank=True, null=True, on_delete=models.CASCADE, related_name='home_fixtures')
    teams_home_winner = models.BooleanField(blank=True, null=True)
    teams_away = models.ForeignKey(LeagueTeams, blank=True, null=True, on_delete=models.CASCADE, related_name='away_fixtures')
    teams_away_winner = models.BooleanField(blank=True, null=True)
    goals = models.JSONField(max_length=250, blank=True, null=True)
    score_halftime = models.JSONField(max_length=250, blank=True, null=True)
    score_fulltime = models.JSONField(max_length=250, blank=True, null=True)
    score_extratime = models.JSONField(max_length=250, blank=True, null=True)
    score_penalty = models.JSONField(max_length=250, blank=True, null=True)


class FixtureStat(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    team = models.ForeignKey(LeagueTeams, on_delete=models.CASCADE)
    ShotsOnGoal = models.IntegerField(blank=True, null=True)
    ShotsOffGoal = models.IntegerField(blank=True, null=True)
    ShotsInsideBox = models.IntegerField(blank=True, null=True)
    ShotsOutsideBox = models.IntegerField(blank=True, null=True)
    TotalShots = models.IntegerField(blank=True, null=True)
    BlockedShots = models.IntegerField(blank=True, null=True)
    Fouls = models.IntegerField(blank=True, null=True)
    CornerKicks = models.IntegerField(blank=True, null=True)
    Offsides = models.IntegerField(blank=True, null=True)
    BallPossession = models.CharField(max_length=10, blank=True, null=True)
    YellowCards = models.IntegerField(blank=True, null=True)
    RedCards = models.IntegerField(blank=True, null=True)
    GoalkeeperSaves = models.IntegerField(blank=True, null=True)
    Totalpasses = models.IntegerField(blank=True, null=True)
    Passesaccurate = models.IntegerField(blank=True, null=True)
    PassesPercent = models.CharField(max_length=10, blank=True, null=True)
    ExpectedGoals = models.FloatField(blank=True, null=True)
    GoalsPrevented = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.fixture.fixture_id} - {self.team.team_name}"
    

class FixtureEvent(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    team = models.ForeignKey(LeagueTeams, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    assist = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='assist_player')
    type = models.CharField(max_length=50)
    detail = models.CharField(max_length=100)
    comments = models.CharField(max_length=200, null=True, blank=True)
    time_elapsed = models.IntegerField()
    time_extra = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.fixture.fixture_id} - {self.team.team_name} - {self.type}"
    



class FixtureLineup(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    team = models.ForeignKey(LeagueTeams, on_delete=models.CASCADE)
    team_color = models.JSONField(blank=True, null=True)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True, blank=True)
    formation = models.CharField(max_length=50)
    start_xi = models.ManyToManyField(Player, related_name='start_xi', blank=True)
    substitutes = models.ManyToManyField(Player, related_name='substitutes', blank=True)

    def __str__(self):
        return f"{self.fixture.fixture_id} - {self.team.team_name}"
    


class FixturePlayer(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    team = models.ForeignKey(LeagueTeams, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    minutes = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    captain = models.BooleanField(default=False)
    substitute = models.BooleanField(default=False)
    shots_total = models.IntegerField(null=True, blank=True)
    shots_on = models.IntegerField(null=True, blank=True)
    goals_total = models.IntegerField(null=True, blank=True)
    goals_conceded = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    saves = models.IntegerField(null=True, blank=True)
    passes_total = models.IntegerField(null=True, blank=True)
    passes_key = models.IntegerField(null=True, blank=True)
    passes_accuracy = models.CharField(max_length=10, null=True, blank=True)
    tackles_total = models.IntegerField(null=True, blank=True)
    blocks = models.IntegerField(null=True, blank=True)
    interceptions = models.IntegerField(null=True, blank=True)
    duels_total = models.IntegerField(null=True, blank=True)
    duels_won = models.IntegerField(null=True, blank=True)
    dribbles_attempts = models.IntegerField(null=True, blank=True)
    dribbles_success = models.IntegerField(null=True, blank=True)
    dribbles_past = models.IntegerField(null=True, blank=True)
    fouls_drawn = models.IntegerField(null=True, blank=True)
    fouls_committed = models.IntegerField(null=True, blank=True)
    cards_yellow = models.IntegerField(null=True, blank=True)
    cards_yellow_red = models.IntegerField(null=True, blank=True)
    cards_red = models.IntegerField(null=True, blank=True)
    penalty_won = models.IntegerField(null=True, blank=True)
    penalty_commited = models.IntegerField(null=True, blank=True)
    penalty_scored = models.IntegerField(null=True, blank=True)
    penalty_missed = models.IntegerField(null=True, blank=True)
    penalty_saved = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.fixture.fixture_id} - {self.team.team_name} - {self.player.name}"