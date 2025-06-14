from rest_framework import serializers
from .models import *
class LeagueSerializer(serializers.ModelSerializer):
    seasons = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ['league_id', 'symbol', 'league_enName', 'league_faName', 'league_type', 'league_logo', 'league_country', 'league_faCountry', 'league_country_flag', 'seasons']

    def get_seasons(self, obj):
        return SeasonSerializer(obj.season_set.select_related('league').all(), many=True).data



class LeagueNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['symbol', 'league_faName', 'league_logo']


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['year']

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('team_id', 'team_name', 'team_faName', 'team_logo', 'team_code', 'team_country', 'team_faCountry', 'team_founded', 'team_national', 'venue')


class TeamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['team_name', 'team_faName', 'team_logo']


class TeamStatSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()  # Use the existing TeamNameSerializer

    class Meta:
        model = TeamStat
        fields = [
            'team', 'form', 'fixtures_played_home', 'fixtures_played_away', 
            'fixtures_played_total', 'wins_home', 'wins_away', 'wins_total', 
            'draws_home', 'draws_away', 'draws_total', 'losses_home', 
            'losses_away', 'losses_total', 'goals_for_home', 'goals_for_away', 
            'goals_for_total', 'goals_against_home', 'goals_against_away', 
            'goals_against_total', 'last_update'
        ]




class CoachSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    career = serializers.JSONField()

    class Meta:
        model = Coach
        fields = ['coach_id', 'name', 'faName', 'age', 'birth_date', 'birth_place', 'birth_faPlace', 'birth_country', 'birth_faCountry', 'nationality', 'faNationality', 'photo', 'team', 'career']



class CoachNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ['name', 'faName']




class AllPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'player_id',
            'name',
            'faName',
        ]


    def get_team(self, obj):
        return {'team_id': obj.team.team_id, 'team_name': obj.team.team_name, 'team_faName': obj.team.team_faName, 'team_logo': obj.team.team_logo}


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'player_id',
            'name',
            'faName',
            'age',
            'birthDate',
            'birthPlace',
            'faBirthPlace',
            'birthCountry',
            'faBirthCountry',
            'nationality',
            'faNationality',
            'height',
            'weight',
            'injured',
            'photo'
        ]

    def get_team(self, obj):
        return {'team_id': obj.team.team_id, 'team_name': obj.team.team_name, 'team_faName': obj.team.team_faName, 'team_logo': obj.team.team_logo}



class PlayerNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name', 'faName']




class PlayerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'name', 'faName', 'age', 'birthDate', 
            'birthPlace', 'faBirthPlace', 'birthCountry', 
            'faBirthCountry', 'nationality', 'faNationality', 
            'height', 'weight', 'injured', 'photo'
            
        ]

        
class SquadSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()

    class Meta:
        model = Squad
        fields = ['player', 'team']

    def get_player(self, squad):
        player = squad.player
        return {
            'id': player.player_id,
            'name': player.name,
            'faName': player.faName,
            'age': player.age,
            'number': getattr(player, 'number', None),  # Assuming 'number' is a custom field, use 'getattr'
            'position': getattr(player, 'position', None),  # Assuming 'position' is also a custom field
            'photo': player.photo,
        }




class PlayerStatSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()
    player = PlayerNameSerializer()
    league_name = serializers.CharField(source='league.league_enName', read_only=True)

    class Meta:
        model = PlayerStat
        fields = [
            'player',
            'team',
            'league', 'league_name', 
            'season',
            'appearances', 'lineups', 'assists',
            'minutes_played', 'rating', 'captain',
            'substitutesIn', 'substitutesOut', 'bench',
            'shotsTotal', 'shotsOn',
            'goalsTotal', 'goalsConceded', 'saves',
            'passTotal', 'passKey', 'passAccuracy',
            'tacklesTotal', 'blocks', 'interceptions',
            'duelsTotal', 'duelsWon', 
            'dribbleAttempts', 'dribbleSuccess', 'dribblePast',
            'foulsDrawn', 'foulsCommitted',
            'cardsYellow', 'cardsYellowRed', 'cardsRed',
            'penaltyWon', 'penaltyCommited', 
            'penaltyScored', 'penaltyMissed', 'penaltySaved'
        ]

class FixtureSerializer(serializers.ModelSerializer):
    league = LeagueNameSerializer()
    season = serializers.SerializerMethodField()
    teams_home = TeamNameSerializer()
    teams_away = TeamNameSerializer()

    class Meta:
        model = Fixture
        fields = [
            'league', 'season', 'fixture_id', 'fixture_referee', 
            'fixture_faReferee', 'fixture_timestamp', 'fixture_periods_first', 
            'fixture_periods_second', 'fixture_venue_name', 'fixture_venue_faName', 
            'fixture_venue_city', 'fixture_venue_faCity', 'fixture_status_long', 
            'fixture_status_short', 'fixture_status_elapsed', 'league_round', 
            'teams_home', 'teams_home_winner', 'teams_away', 'teams_away_winner', 
            'goals', 'score_halftime', 'score_fulltime', 'score_extratime', 'score_penalty'
        ]

    def get_season(self, obj):
        return {'year': obj.season.year}










class TopScoreSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()  # Include the team serializer
    player = serializers.SerializerMethodField()
    class Meta:
        model = PlayerStat
        fields = ['player', 'goalsTotal', 'team']  # Include 'team' in the fields list
    def get_player(self, obj):
        return PlayerNameSerializer(obj.player).data




class TopAssistSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()  # Include the team serializer
    player = serializers.SerializerMethodField()
    class Meta:
        model = PlayerStat
        fields = ['player', 'assists', 'team']  # Include 'team' in the fields list
    def get_player(self, obj):
        return PlayerNameSerializer(obj.player).data




class TopYellowCardSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()  # Include the team serializer
    player = serializers.SerializerMethodField()
    class Meta:
        model = PlayerStat
        fields = ['player', 'cardsYellow', 'team']  # Include 'team' in the fields list
    def get_player(self, obj):
        return PlayerNameSerializer(obj.player).data
    



class TopRedCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStat
        fields = ['player', 'cardsRed']  # Ensure this matches your model field name

    player = serializers.SerializerMethodField()

    def get_player(self, obj):
        from .serializers import PlayerNameSerializer
        return PlayerNameSerializer(obj.player).data
    




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



class FixtureLineupPlayerSerializer(serializers.ModelSerializer):
    player = PlayerNameSerializer()  # Or your preferred Player serializer

    class Meta:
        model = FixtureLineupPlayer
        fields = ['player', 'is_starting', 'pos', 'grid', 'number']

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
        return obj.coach.name if obj.coach else None

    def get_start_xi(self, obj):
        lineup_players = obj.lineup_players.filter(is_starting=True)
        return FixtureLineupPlayerSerializer(lineup_players, many=True).data

    def get_substitutes(self, obj):
        lineup_players = obj.lineup_players.filter(is_starting=False)
        return FixtureLineupPlayerSerializer(lineup_players, many=True).data

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
        return obj.league.league_enName if obj.league else None

    def get_league_faName(self, obj):
        return obj.league.league_faName if obj.league else None

class TableSerializer(serializers.ModelSerializer):
    team = TeamNameSerializer()  # Use the existing TeamNameSerializer

    class Meta:
        model = Table
        fields = ['team', 'rank', 'points', 'goals_diff', 
                  'group', 'form', 'status', 'description', 'played', 
                  'win', 'draw', 'lose', 'goals_for', 'goals_against', 'last_update']
        
class TransferSerializer(serializers.ModelSerializer):
    player = PlayerNameSerializer()
    team_in = TeamNameSerializer()  # Include the incoming team serializer
    team_out = TeamNameSerializer()  # Include the outgoing team serializer
    class Meta:
        model = Transfer
        fields = ['player', 'team_in', 'team_out', 'transfer_date', 'transfer_type', 'update_time']
    def get_player(self, obj):
        return PlayerNameSerializer(obj.player).data