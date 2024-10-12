from rest_framework import serializers
from .models import Leagues, Season, LeagueTeams , Player, Fixture, FixtureStat , FixtureEvent, Coach, FixtureLineup, FixturePlayer
import re


class LeagueSerializer(serializers.ModelSerializer):
    seasons = serializers.SerializerMethodField()

    class Meta:
        model = Leagues
        fields = ['league_id', 'league_name', 'league_enName', 'league_faName', 'league_type', 'league_logo', 'league_country', 'league_country_flag', 'seasons']

    def get_seasons(self, obj):
        return SeasonSerializer(obj.season_set.select_related('league').all(), many=True).data
    

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['year', 'start', 'end']
        

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeagueTeams
        fields = ('team_id', 'team_name', 'team_faName', 'team_logo', 'team_code', 'team_country', 'team_faCountry', 'team_founded', 'team_national', 'venue', 'league_id')



class TeamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeagueTeams
        fields = ['team_name', 'team_faName']



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
    teams_home = serializers.SerializerMethodField()
    teams_away = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()

    class Meta:
        model = Fixture
        fields = '__all__'

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

    def get_season(self, obj):
        return obj.season.year



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
        fields = ['ShotsOnGoal', 'ShotsOffGoal', 'ShotsInsideBox', 'ShotsOutsideBox', 'TotalShots', 'BlockedShots', 'Fouls', 'CornerKicks', 'Offsides', 'BallPossession', 'YellowCards', 'RedCards', 'GoalkeeperSaves', 'Totalpasses', 'Passesaccurate', 'PassesPercent', 'ExpectedGoals', 'GoalsPrevented', 'fixture', 'team']



class FixtureEventSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    player = PlayerNameSerializer()
    assist = PlayerNameSerializer()

    class Meta:
        model = FixtureEvent
        fields = ['fixture', 'team', 'player', 'assist', 'type', 'detail', 'comments', 'time_elapsed', 'time_extra']



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
        return [{'name': player.name, 'faName': player.faName,'number': player.number, 'position': player.position, 'grid': player.grid} for player in obj.start_xi.all()]

    def get_substitutes(self, obj):
        return [{'name': player.name, 'faName': player.faName,'number': player.number, 'position': player.position, 'grid': player.grid} for player in obj.substitutes.all()]
    

class FixturePlayerSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    player = PlayerNameSerializer()

    class Meta:
        model = FixturePlayer
        fields = ['fixture', 'team', 'player', 'minutes', 'rating', 'captain', 'substitute', 'shots_total', 'shots_on', 'goals_total', 'goals_conceded', 'assists', 'saves', 'passes_total', 'passes_key', 'passes_accuracy', 'tackles_total', 'blocks', 'interceptions', 'duels_total', 'duels_won', 'dribbles_attempts', 'dribbles_success', 'dribbles_past', 'fouls_drawn', 'fouls_committed', 'cards_yellow', 'cards_yellow_red', 'cards_red', 'penalty_won', 'penalty_commited', 'penalty_scored', 'penalty_missed', 'penalty_saved']