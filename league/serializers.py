from rest_framework import serializers
from .models import League, Season, Team , TeamLeague, Player, Fixture, FixtureStat , FixtureEvent, Coach, FixtureLineup, FixturePlayer

class LeagueSerializer(serializers.ModelSerializer):
    seasons = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ['league_id', 'league_name', 'league_enName', 'league_faName', 'league_type', 'league_logo', 'league_country', 'league_faCountry', 'league_country_flag', 'seasons']

    def get_seasons(self, obj):
        return SeasonSerializer(obj.season_set.select_related('league').all(), many=True).data

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['year']

from rest_framework import serializers

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('team_id', 'team_name', 'team_faName', 'team_logo', 'team_code', 'team_country', 'team_faCountry', 'team_founded', 'team_national', 'venue')


class TeamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['team_name', 'team_faName', 'team_logo']



class CoachSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    career = serializers.JSONField()

    class Meta:
        model = Coach
        fields = ['coach_id', 'name', 'faName', 'age', 'birth_date', 'birth_place', 'birth_faPlace', 'birth_country', 'birth_faCountry', 'nationality', 'faNationality', 'photo', 'team', 'career']

class PlayerSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    class Meta:
        model = Player
        fields = ['player_id', 'name', 'faName', 'age', 'birthDate', 'birthPlace', 'faBirthPlace', 'birthCountry', 'faBirthCountry', 'nationality', 'faNationality', 'height', 'weight', 'injured', 'photo', 'team', 'appearences', 'lineups', 'minutes', 'number', 'position', 'rating', 'captain', 'substitutesIn', 'substitutesOut', 'bench', 'shotsTotal', 'shotsOn', 'goalsTotal', 'goalsConceded', 'assists', 'saves', 'passTotal', 'passKey', 'passAccuracy', 'tacklesTotal', 'blocks', 'interceptions', 'duelsTotal', 'duelsWon', 'dribbleAttempts', 'dribbleSuccess', 'dribblePast', 'foulsDrawn', 'foulsCommitted', 'cardsYellow', 'cardsYellowRed', 'cardsRed', 'penaltyWon', 'penaltyCommited', 'penaltyScored', 'penaltyMissed', 'penaltySaved']

    def get_team(self, obj):
        return {'team_id': obj.team.team_id, 'team_name': obj.team.team_name, 'team_faName': obj.team.team_faName, 'team_logo': obj.team.team_logo}



class FixtureSerializer(serializers.ModelSerializer):
    league = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()
    teams_home = TeamNameSerializer()
    teams_away = TeamNameSerializer()

    class Meta:
        model = Fixture
        fields = ['league', 'season', 'fixture_id', 'fixture_referee', 
                  'fixture_faReferee', 'fixture_timestamp', 'fixture_periods_first', 
                  'fixture_periods_second', 'fixture_venue_name', 'fixture_venue_faName', 
                  'fixture_venue_city', 'fixture_venue_faCity', 'fixture_status_long', 
                  'fixture_status_short', 'fixture_status_elapsed', 'league_round', 
                  'teams_home', 'teams_home_winner', 'teams_away', 'teams_away_winner', 
                  'goals', 'score_halftime', 'score_fulltime', 'score_extratime', 'score_penalty']

    def get_league(self, obj):
        return {
            'id': obj.league.league_id,
            'name': obj.league.league_name,
            'faName': obj.league.league_faName,
            'logo': obj.league.league_logo  # Add the league_logo here
        }

    def get_season(self, obj):
        return {
            'year': obj.season.year
        }

    def get_teams_home(self, obj):
        return {
            'team_id': obj.teams_home.team_id,
            'team_name': obj.teams_home.team_name,
            'team_faName': obj.teams_home.team_faName,
        }

    def get_teams_away(self, obj):
        return {
            'team_id': obj.teams_away.team_id,
            'team_name': obj.teams_away.team_name,
            'team_faName': obj.teams_away.team_faName,
        }



class PlayerNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name', 'faName']



class CoachNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ['name', 'faName']

class FixtureStatSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    class Meta:
        model = FixtureStat
        fields = [
            'fixture', 'team', 'ShotsOnGoal', 'ShotsOffGoal', 
            'ShotsInsideBox', 'ShotsOutsideBox', 'TotalShots', 
            'BlockedShots', 'Fouls', 'CornerKicks', 'Offsides', 
            'BallPossession', 'YellowCards', 'RedCards', 
            'GoalkeeperSaves', 'Totalpasses', 'Passesaccurate', 
            'PassesPercent', 'ExpectedGoals', 'GoalsPrevented'
        ]




class FixtureEventSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    player = PlayerNameSerializer()
    assist = PlayerNameSerializer()

    class Meta:
        model = FixtureEvent
        fields = ['fixture', 'team', 'player', 'assist', 'type', 
                  'detail', 'comments', 'time_elapsed', 'time_extra']



class FixtureLineupSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    coach = serializers.SerializerMethodField()
    start_xi = serializers.SerializerMethodField()
    substitutes = serializers.SerializerMethodField()

    class Meta:
        model = FixtureLineup
        fields = ['fixture', 'team', 'coach', 'formation', 'start_xi', 'substitutes']

    def get_team(self, obj):
        return {'team_name': obj.team.team_name, 'team_faName': obj.team.team_faName}

    def get_coach(self, obj):
        return obj.coach.name

    def get_start_xi(self, obj):
        return [{'name': player.name, 'faName': player.faName,'number': player.number, 
                 'position': player.position, 'grid': player.grid} for player in obj.start_xi.all()]

    def get_substitutes(self, obj):
        return [{'name': player.name, 'faName': player.faName,'number': player.number, 
                 'position': player.position, 'grid': player.grid} for player in obj.substitutes.all()]
    

class FixturePlayerSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    player = PlayerNameSerializer()

    class Meta:
        model = FixturePlayer
        fields = ['fixture', 'team', 'player', 'minutes', 'rating',
                   'captain', 'substitute', 'shots_total', 'shots_on', 
                   'goals_total', 'goals_conceded', 'assists', 'saves', 
                   'passes_total', 'passes_key', 'passes_accuracy', 
                   'tackles_total', 'blocks', 'interceptions', 'duels_total', 
                   'duels_won', 'dribbles_attempts', 'dribbles_success', 
                   'dribbles_past', 'fouls_drawn', 'fouls_committed', 'cards_yellow', 
                   'cards_yellow_red', 'cards_red', 'penalty_won', 'penalty_commited', 
                   'penalty_scored', 'penalty_missed', 'penalty_saved']



class FixtureH2HSerializer(serializers.ModelSerializer):
    league_name = serializers.SerializerMethodField()
    league_faName = serializers.SerializerMethodField()
    teams_home = TeamNameSerializer()
    teams_away = TeamNameSerializer()

    class Meta:
        model = Fixture
        fields = ['fixture_id', 'fixture_timestamp', 'league_name',
            'league_faName', 'teams_home', 'teams_away', 'score_fulltime',
            'score_extratime', 'score_penalty',
        ]

    def get_league_name(self, obj):
        return obj.league.league_name if obj.league else None

    def get_league_faName(self, obj):
        return obj.league.league_faName if obj.league else None

