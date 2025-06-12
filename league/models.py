from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

class League(models.Model):
    league_id = models.IntegerField(primary_key=True)
    symbol = models.CharField(max_length=500, blank=True, null=True) 
    league_enName = models.CharField(max_length=500, blank=True, null=True) 
    league_faName = models.CharField(max_length=500, blank=True, null=True) 
    league_type = models.CharField(max_length=50, blank=True, null=True)
    league_logo = models.URLField(blank=True, null=True)
    league_country = models.JSONField()
    league_faCountry = models.CharField(max_length=500, blank=True, null=True)
    league_country_flag = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.league_enName

class Season(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    year = models.IntegerField()

class Team(models.Model):
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

class TeamLeague(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'league', 'season')  # Ensure a team can only be linked to a league in a specific season once
    


class TeamStat(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='team_stats')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_stats')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='team_stats')

    form = models.CharField(max_length=50, null=True, blank=True)

    fixtures_played_home = models.IntegerField(default=0)
    fixtures_played_away = models.IntegerField(default=0)
    fixtures_played_total = models.IntegerField(default=0)
    
    wins_home = models.IntegerField(default=0)
    wins_away = models.IntegerField(default=0)
    wins_total = models.IntegerField(default=0)
    
    draws_home = models.IntegerField(default=0)
    draws_away = models.IntegerField(default=0)
    draws_total = models.IntegerField(default=0)
    
    losses_home = models.IntegerField(default=0)
    losses_away = models.IntegerField(default=0)
    losses_total = models.IntegerField(default=0)
    
    goals_for_home = models.IntegerField(default=0)
    goals_for_away = models.IntegerField(default=0)
    goals_for_total = models.IntegerField(default=0)

    goals_against_home = models.IntegerField(default=0)
    goals_against_away = models.IntegerField(default=0)
    goals_against_total = models.IntegerField(default=0)

    clean_sheet_home = models.IntegerField(default=0)
    clean_sheet_away = models.IntegerField(default=0)
    clean_sheet_total = models.IntegerField(default=0)

    failed_to_score_home = models.IntegerField(default=0)
    failed_to_score_away = models.IntegerField(default=0)
    failed_to_score_total = models.IntegerField(default=0)

    penalties_scored_total = models.IntegerField(default=0)
    penalties_missed_total = models.IntegerField(default=0)

    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team.team_name} Stats for {self.season.year} in {self.league.league_enName}"




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
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    career = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name



class Player(models.Model):
    POSITION_CHOICES = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Defender', 'Defender'),
        ('Midfielder', 'Midfielder'),
        ('Attacker', 'Attacker'),
        (None, 'Unknown'),
    ]
    POS_MAP = {
        "G": "Goalkeeper",
        "D": "Defender",
        "M": "Midfielder",
        "F": "Attacker"
    }

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
    number = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, blank=True, null=True)
    photo = models.URLField(blank=True, null=True)

    def set_position_from_short(self, pos_short):
        self.position = self.POS_MAP.get(pos_short, None)

    def __str__(self):
        return self.name

class PlayerTeam(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'team', 'season')

    def __str__(self):
        return f"{self.player.name} - {self.team.name} ({self.season.year})"

class Squad(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='squads')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='squads')

    class Meta:
        unique_together = ('player', 'team')  # Ensure unique combination of player and team

    def __str__(self):
        return f"{self.player.name} in {self.team.team_name}"
    


class PlayerStat(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='player_stats')
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    league = models.ForeignKey('League', on_delete=models.CASCADE)
    season = models.IntegerField(validators=[MinValueValidator(1900)])
    
    # Game statistics
    appearances = models.IntegerField(default=0, null=True)
    lineups = models.IntegerField(default=0, null=True)
    minutes_played = models.IntegerField(default=0, null=True)
    rating = models.FloatField(null=True, blank=True)
    captain = models.BooleanField(default=False)
    
    # Substitution details
    substitutesIn = models.IntegerField(default=0, null=True)
    substitutesOut = models.IntegerField(default=0, null=True)
    bench = models.IntegerField(default=0, null=True)
    
    # Goal-related stats
    assists = models.IntegerField(default=0, null=True)
    goalsTotal = models.IntegerField(default=0, null=True)
    goalsConceded = models.IntegerField(default=0, null=True)
    saves = models.IntegerField(default=0, null=True)
    
    # Shooting stats
    shotsTotal = models.IntegerField(default=0, null=True)
    shotsOn = models.IntegerField(default=0, null=True)
    
    # Passing stats
    passTotal = models.IntegerField(default=0, null=True)
    passKey = models.IntegerField(default=0, null=True)
    passAccuracy = models.FloatField(null=True, blank=True)
    
    # Defensive stats
    tacklesTotal = models.IntegerField(default=0, null=True)
    blocks = models.IntegerField(default=0, null=True)
    interceptions = models.IntegerField(default=0, null=True)
    
    # Duels and dribbling
    duelsTotal = models.IntegerField(default=0, null=True)
    duelsWon = models.IntegerField(default=0, null=True)
    dribbleAttempts = models.IntegerField(default=0, null=True)
    dribbleSuccess = models.IntegerField(default=0, null=True)
    dribblePast = models.IntegerField(default=0, null=True)
    
    # Fouls and cards
    foulsDrawn = models.IntegerField(default=0, null=True)
    foulsCommitted = models.IntegerField(default=0, null=True)
    cardsYellow = models.IntegerField(default=0, null=True)
    cardsYellowRed = models.IntegerField(default=0, null=True)
    cardsRed = models.IntegerField(default=0, null=True)
    
    # Penalty stats
    penaltyWon = models.IntegerField(default=0, null=True)
    penaltyCommited = models.IntegerField(default=0, null=True)
    penaltyScored = models.IntegerField(default=0, null=True)
    penaltyMissed = models.IntegerField(default=0, null=True)
    penaltySaved = models.IntegerField(default=0, null=True)

    class Meta:
        unique_together = ['player', 'team', 'league', 'season']

    def __str__(self):
        return f"{self.player.name} - {self.team.team_name} - {self.season}"



class Fixture(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='fixtures')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='fixtures')
    fixture_id = models.IntegerField(primary_key=True, unique=True)
    fixture_referee = models.CharField(max_length=250, blank=True, null=True)
    fixture_faReferee = models.CharField(max_length=250, blank=True, null=True)
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
    fixture_status_extra = models.CharField(max_length=250, blank=True, null=True)
    league_round = models.CharField(max_length=100)
    teams_home = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE, related_name='home_fixtures')
    teams_home_winner = models.BooleanField(blank=True, null=True)
    teams_away = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE, related_name='away_fixtures')
    teams_away_winner = models.BooleanField(blank=True, null=True)
    goals = models.JSONField(max_length=250, blank=True, null=True)
    score_halftime = models.JSONField(max_length=250, blank=True, null=True)
    score_fulltime = models.JSONField(max_length=250, blank=True, null=True)
    score_extratime = models.JSONField(max_length=250, blank=True, null=True)
    score_penalty = models.JSONField(max_length=250, blank=True, null=True)

class FixtureRound(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    rounds = models.JSONField()  # Store the rounds as a JSON field

    def __str__(self):
        return f"{self.league} - {self.season.year}"
    


class FixtureStat(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
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
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
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
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    team_color = models.JSONField(null=True, blank=True)
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True)
    formation = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.team.team_name} ({self.fixture.fixture_id})"

class FixtureLineupPlayer(models.Model):
    fixture_lineup = models.ForeignKey(FixtureLineup, on_delete=models.CASCADE, related_name='lineup_players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_starting = models.BooleanField()  # True for startXI, False for substitutes
    pos = models.CharField(max_length=2, null=True, blank=True)  # "G", "D", "M", "F"
    grid = models.CharField(max_length=10, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player.name} ({'XI' if self.is_starting else 'Sub'})"

class FixturePlayer(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    minutes = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    captain = models.BooleanField(default=False)
    substitute = models.BooleanField(default=False)
    number = models.IntegerField(null=True, blank=True)  # <-- add this
    position = models.CharField(max_length=10, null=True, blank=True)  # <-- add this
    offsides = models.IntegerField(null=True, blank=True)  # <-- add this
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



class Table(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    rank = models.IntegerField()
    points = models.IntegerField()
    goals_diff = models.IntegerField()
    group = models.CharField(max_length=100)
    form = models.CharField(max_length=50)
    status = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    played = models.IntegerField()
    win = models.IntegerField()
    draw = models.IntegerField()
    lose = models.IntegerField()
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()
    last_update = models.DateTimeField()

    def __str__(self):
        return f"{self.team.team_name} - {self.season.year} - {self.league.league_enName}"
    



class Transfer(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='transfers')  # Link to Player model
    team_in = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='incoming_transfers')  # Team the player is coming to
    team_out = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='outgoing_transfers')  # Team the player is leaving
    transfer_date = models.DateField()
    transfer_type = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Loan", "Transfer", etc.
    update_time = models.DateTimeField(auto_now=True)  # To track when the transfer was last updated

    def __str__(self):
        return f"{self.player.name} transfer to {self.team_in.team_name} from {self.team_out.team_name} on {self.transfer_date}"
