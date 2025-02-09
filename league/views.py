import logging
from googletrans import Translator
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import League, Season, Team, TeamLeague, Coach, Player, Fixture, FixtureRound, FixtureStat, FixtureEvent, FixtureLineup, FixturePlayer
from .serializers import LeagueSerializer, TeamSerializer, CoachSerializer, PlayerSerializer, FixtureSerializer, FixtureStatSerializer, FixtureEventSerializer, FixtureLineupSerializer, FixturePlayerSerializer, FixtureH2HSerializer
from .last import accheaders, myleague_ids, get_year, get_today_date
from urllib.parse import unquote



logger = logging.getLogger(__name__)



class LeagueListView(APIView):
    def get(self, request):
        # Return the keys of myleague_ids
        supported_leagues = list(myleague_ids.keys())
        return Response({"supported_leagues": supported_leagues})

class LeagueView(APIView):
    def get(self, request, league):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league3"}, status=400)

        return self.get_league_data(league_id)

    def get_league_data(self, league_id):
        try:
            league_data = League.objects.get(league_id=league_id)
            serializer = LeagueSerializer(league_data)
            return Response(serializer.data)
        except League.DoesNotExist:
            return self.fetch_league_data_from_api(league_id)

    def fetch_league_data_from_api(self, league_id):
        url = f'https://v3.football.api-sports.io/leagues?id={league_id}'
        headers = accheaders
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()['response'][0]
            league_name = data['league']['name']
            league_enName = league_name.lower()

            # Using googletrans for translation
            translator = Translator()
            league_faName = translator.translate(league_name, dest='fa').text
            country_name = data['country']['name']
            league_faCountry = translator.translate(country_name, dest='fa').text  # Translate country name to Persian

            with transaction.atomic():
                league_data = League.objects.create(
                    league_id=league_id,
                    league_name=league_name,
                    league_enName=league_enName,
                    league_faName=league_faName,
                    league_type=data['league']['type'],
                    league_logo=data['league']['logo'],
                    league_country=data['country'],
                    league_faCountry = league_faCountry,
                    league_country_flag=data['country']['flag'],
                )
                if 'seasons' in data:
                    seasons = []
                    for season in data['seasons']:
                        seasons.append(Season(
                            league=league_data,
                            year=season['year'],
                        ))
                    Season.objects.bulk_create(seasons)

            # Prepare the response data
            response_data = {
                "league_id": league_data.league_id,
                "league_name": league_data.league_name,
                "league_enName": league_data.league_enName,
                "league_faName": league_data.league_faName,
                "league_type": league_data.league_type,
                "league_logo": league_data.league_logo,
                "faCountry": league_faCountry,
                "league_country": {
                    "code": data['country']['code'],
                    "flag": data['country']['flag'],
                    "name": country_name,
                      # Add the translated country name here
                },
                "league_country_flag": league_data.league_country_flag,
            }

            # Add seasons to the response if needed
            if hasattr(league_data, 'seasons'):
                response_data['seasons'] = [{"year": season.year} for season in league_data.seasons.all()]

            return Response(response_data)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch league data: " + str(e)}, status=500)
        except Exception as e:
            return Response({"error": "Failed to fetch league data: " + str(e)}, status=500)


class TeamView(APIView):
    def get(self, request, league, season=None):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        
        if league_id is None:
            return Response({"error": "Invalid league6"}, status=400)

        if season is None:
            season = str(get_year())

        # Check if the league exists in the database
        if not League.objects.filter(league_id=league_id).exists():
            # If league_id exists in myleague_ids, fetch from API and save it
            league_response = LeagueView().fetch_league_data_from_api(league_id)
            if league_response.status_code != 200:
                return league_response  # Return the error response from LeagueView

        try:
            league_data = League.objects.get(league_id=league_id)
            season_data = Season.objects.filter(league=league_data, year=season)

            if not season_data.exists():
                return Response({"error": "Invalid season"}, status=400)

            teams = TeamLeague.objects.filter(league=league_data, season__in=season_data).select_related('team')
            if teams.exists():
                serializer = TeamSerializer([team_league.team for team_league in teams], many=True)
                return Response(serializer.data)
            else:
                return self.get_teams_from_api(request, league_id, season)
        except League.DoesNotExist:
            return Response({"error": "League data not found"}, status=404)

    def get_teams_from_api(self, request, league_id, season):
        url = f'https://v3.football.api-sports.io/teams?league={league_id}&season={season}'
        headers = accheaders
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()['response']
            teams = []
            translator = Translator()
            for team in data:
                team_faName = translator.translate("The " + team['team']['name'], src='en', dest='fa').text
                team_country_faName = translator.translate(team['team']['country'], src='en', dest='fa').text
                venue_faName = translator.translate(team['venue']['name'], src='en',  dest='fa').text
                city_fa = translator.translate(team['venue']['city'], dest='fa').text
                
                team_data, created = Team.objects.get_or_create(
                    team_id=team['team']['id'],
                    defaults={
                        'team_name': team['team']['name'],
                        'team_faName': team_faName,
                        'team_logo': team['team']['logo'],
                        'team_code': team['team']['code'],
                        'team_country': team['team']['country'],
                        'team_faCountry': team_country_faName,
                        'team_founded': team['team']['founded'],
                        'team_national': team['team']['national'],
                        'venue': {
                            'name': team['venue']['name'],
                            'venue_faName': venue_faName,
                            'address': team['venue']['address'],
                            'city': team['venue']['city'],
                            'city_fa': city_fa,
                            'capacity': team['venue']['capacity'],
                            'image': team['venue']['image'],
                        },
                    }
                )

                # Create or update the TeamLeague relationship
                season_instance = Season.objects.get(league_id=league_id, year=season)
                TeamLeague.objects.get_or_create(team=team_data, league_id=league_id, season=season_instance)

                teams.append(team_data)

            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch team data"}, status=response.status_code)

class CoachView(APIView):
    def get(self, request, team_id):
        try:
            team_data = Team.objects.get(team_id=team_id)
            coaches = Coach.objects.filter(team=team_data)
            if coaches.exists():
                serializer = CoachSerializer(coaches, many=True)
                return Response(serializer.data)
            else:
                return self.get_coaches_from_api(team_id)
        except Team.DoesNotExist:
            return Response({"error": "Team data not found"}, status=404)

    def get_coaches_from_api(self, team_id):
        url = f'https://v3.football.api-sports.io/coachs?team={team_id}'
        headers = accheaders
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()['response']
            coaches = []
            translator = Translator()
            
            for coach in data:
                # Extract last name from the full name
                full_name = coach['name']
                last_name = "Mr."+full_name.split()[-1]  # Get the last part of the name
                
                # Translate last name to Persian
                last_name_fa = translator.translate(last_name,src='en', dest='fa').text
                lastNameFa = last_name_fa.split()[-1]
                
                # Translate other details
                birth_faPlace = translator.translate(coach['birth']['place'], dest='fa').text
                birth_faCountry = translator.translate(coach['birth']['country'], dest='fa').text
                nationality_fa = translator.translate(coach['nationality'], dest='fa').text
                
                try:
                    team = Team.objects.get(team_id=team_id)
                except Team.DoesNotExist:
                    return Response({"error": "Team data not found"}, status=404)

                career = []
                for career_data in coach['career']:
                    career.append({
                        "team": career_data['team']['name'],
                        "start": career_data['start'],
                        "end": career_data['end']
                    })
                    
                coach_data, created = Coach.objects.get_or_create(
                    coach_id=coach['id'],
                    defaults={
                        'name': full_name,
                        'faName': lastNameFa,  # Use translated last name
                        'age': coach['age'],
                        'birth_date': coach['birth']['date'],
                        'birth_place': coach['birth']['place'],
                        'birth_faPlace': birth_faPlace,
                        'birth_country': coach['birth']['country'],
                        'birth_faCountry': birth_faCountry,
                        'nationality': coach['nationality'],
                        'faNationality': nationality_fa,
                        'photo': coach['photo'],
                        'team': team,
                        'career': career
                    }
                )
                coaches.append(coach_data)
            
            serializer = CoachSerializer(coaches, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch coach data"}, status=response.status_code)



class PlayerView(APIView):
    def get(self, request, league, team_id, season=None):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league4"}, status=400)

        if season is None:
            season = str(get_year())

        try:
            league_data = League.objects.get(league_id=league_id)
            season_data = Season.objects.get(league=league_data, year=season)
            # Use TeamLeague to find the team in the specified league
            team_data = TeamLeague.objects.get(team__team_id=team_id, league=league_data, season=season_data).team
        except (League.DoesNotExist, Season.DoesNotExist, TeamLeague.DoesNotExist):
            return Response({"error": "Invalid league, season or team"}, status=400)

        try:
            players = Player.objects.filter(team=team_data, season=season_data)
            if players.exists():
                serializer = PlayerSerializer(players, many=True)
                return Response(serializer.data)
            else:
                return self.get_players_from_api(request, league_id, team_id, season, team_data, season_data)
        except Player.DoesNotExist:
            return self.get_players_from_api(request, league_id, team_id, season, team_data, season_data)

    def get_players_from_api(self, request, league_id, team_id, season, team_data, season_data):
        url = f"https://v3.football.api-sports.io/players?league={league_id}&season={season}&team={team_id}"
        headers = accheaders

        # Create a Session object
        session = requests.Session()
        session.headers.update(headers)

        response = session.get(url)
        print(response.status_code)

        if response.status_code == 200:
            data = response.json()
            players = []
            translator = Translator()

            # Get the total number of pages
            total_pages = data['paging']['total']

            # Fetch all pages of players
            for page in range(1, total_pages + 1):
                page_url = f"{url}&page={page}"
                page_response = session.get(page_url)
                page_data = page_response.json()

                # Loop through each player in the response
                for player_data in page_data['response']:
                    player = player_data['player']
                    statistics = player_data['statistics'][0]

                    # Create a dictionary to store the player data
                    name_parts = player['name'].split()
                    firstname_parts = player['firstname'].split()

                    if len(firstname_parts) == 1:
                        name = f"{firstname_parts[0]} {name_parts[-1]}"
                    else:
                        for part in firstname_parts:
                            if part[0].lower() == name_parts[0][0].lower():
                                name = f"{part} {name_parts[-1]}"
                                break
                        else:
                            name = f"{firstname_parts[0]} {name_parts[-1]}"

                    player_dict = {
                        'player_id': player['id'],
                        'name': name,
                        'faName': translator.translate(name, src='en', dest='fa').text,
                        'age': player['age'],
                        'birthDate': player['birth']['date'],
                        'birthPlace': player['birth']['place'],
                        'faBirthPlace': translator.translate(player['birth']['place'], dest='fa').text,
                        'birthCountry': player['birth']['country'],
                        'faBirthCountry': translator.translate(player['birth']['country'], dest='fa').text,
                        'nationality': player['nationality'],
                        'faNationality': translator.translate(player['nationality'], dest='fa').text,
                        'height': player['height'],
                        'weight': player['weight'],
                        'injured': player['injured'],
                        'photo': player['photo'],
                        'team': team_data,
                        'season': season_data,
                        'appearences': statistics['games']['appearences'],
                        'lineups': statistics['games']['lineups'],
                        'minutes': statistics['games']['minutes'],
                        'number': statistics['games']['number'],
                        'position': statistics['games']['position'],
                        'rating': statistics['games']['rating'],
                        'captain': statistics['games']['captain'],
                        'substitutesIn': statistics['substitutes']['in'],
                        'substitutesOut': statistics['substitutes']['out'],
                        'bench': statistics['substitutes']['bench'],
                        'shotsTotal': statistics['shots']['total'],
                        'shotsOn': statistics['shots']['on'],
                        'goalsTotal': statistics['goals']['total'],
                        'goalsConceded': statistics['goals']['conceded'],
                        'assists': statistics['goals']['assists'],
                        'saves': statistics['goals']['saves'],
                        'passTotal': statistics['passes']['total'],
                        'passKey': statistics['passes']['key'],
                        'passAccuracy': statistics['passes']['accuracy'],
                        'tacklesTotal': statistics['tackles']['total'],
                        'blocks': statistics['tackles']['blocks'],
                        'interceptions': statistics['tackles']['interceptions'],
                        'duelsTotal': statistics['duels']['total'],
                        'duelsWon': statistics['duels']['won'],
                        'dribbleAttempts': statistics['dribbles']['attempts'],
                        'dribbleSuccess': statistics['dribbles']['success'],
                        'dribblePast': statistics['dribbles']['past'],
                        'foulsDrawn': statistics['fouls']['drawn'],
                        'foulsCommitted': statistics['fouls']['committed'],
                        'cardsYellow': statistics['cards']['yellow'],
                        'cardsYellowRed': statistics['cards']['yellowred'],
                        'cardsRed': statistics['cards']['red'],
                        'penaltyWon': statistics['penalty']['won'],
                        'penaltyCommited': statistics['penalty']['commited'],
                        'penaltyScored': statistics['penalty']['scored'],
                        'penaltyMissed': statistics['penalty']['missed'],
                        'penaltySaved': statistics['penalty']['saved'],
                    }

                    # Create or update the player in the database
                    player_obj, created = Player.objects.get_or_create(player_id=player['id'], defaults=player_dict)
                    if not created:
                        # If the player already exists, update its data
                        for key, value in player_dict.items():
                            setattr(player_obj, key, value)
                        player_obj.save()

                    players.append(player_obj)

            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch player data"}, status=response.status_code)
        


class FixtureView(APIView):
    def get(self, request, league, season=None):
        try:
            # If no season provided, use current year
            if season is None:
                season = str(get_year())
            
            # Check if league is supported
            league_id = myleague_ids.get(league)
            if league_id is None:
                return Response(
                    {"error": "Invalid league5"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ensure league exists
            try:
                league_data = League.objects.get(league_id=league_id)
            except League.DoesNotExist:
                from .views import LeagueView
                league_response = LeagueView().fetch_league_data_from_api(league_id)
                if league_response.status_code != 200:
                    return league_response
                league_data = League.objects.get(league_id=league_id)
            
            # Ensure season exists
            try:
                season_data = Season.objects.get(league=league_data, year=season)
            except Season.DoesNotExist:
                return Response(
                    {"error": "Invalid season"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if fixtures exist
            fixtures = Fixture.objects.filter(league=league_data, season=season_data)
            
            if fixtures.exists():
                # Retrieve fixture rounds
                try:
                    fixture_rounds = FixtureRound.objects.get(
                        league=league_data, 
                        season=season_data
                    )
                    rounds_dict = fixture_rounds.rounds
                except FixtureRound.DoesNotExist:
                    rounds_dict = {}
                
                serializer = FixtureSerializer(fixtures, many=True)
                return Response({
                    'fixtures': serializer.data,
                    'rounds': rounds_dict
                })
            else:
                # If no fixtures, fetch from API
                return self.get_fixtures_from_api(league_id, season)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_fixtures_from_api(self, league_id, season):
        try:
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
            headers = accheaders
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            fixtures_data = response.json()['response']
            
            # Ensure teams exist
            self.ensure_teams_exist(league_id, season, fixtures_data)
            
            # Prepare translators
            translator = Translator()
            
            # Prepare translation collections
            referee_translations = {}
            venue_name_translations = {}
            venue_city_translations = {}
            round_translations = {}
            
            # Collect unique values for translation
            for fixture in fixtures_data:
                # Handle referee translations
                referee = fixture['fixture']['referee']
                if referee:
                    referee_translations[referee] = "The " + str(referee)
                
                # Handle venue name translations
                venue_name = fixture['fixture']['venue']['name']
                if venue_name:
                    venue_name_translations[venue_name] = "The " + str(venue_name)
                
                # Handle venue city translations
                venue_city = fixture['fixture']['venue']['city']
                if venue_city:
                    venue_city_translations[venue_city] = "The " + str(venue_city)
                
                # Handle round translations
                round_name = fixture['league']['round']
                if round_name:
                    if 'Regular Season' in round_name:
                        round_name = round_name.replace('Regular Season', 'week')
                    round_translations[round_name] = round_name
                else:
                    round_name = 'Unknown Round'
                    round_translations[round_name] = round_name
            
            # Bulk translate
            referee_fa_translations = {
                k: translator.translate(v, dest='fa').text 
                for k, v in referee_translations.items()
            } if referee_translations else {}
            
            venue_name_fa_translations = {
                k: translator.translate(v, dest='fa').text 
                for k, v in venue_name_translations.items()
            } if venue_name_translations else {}
            
            venue_city_fa_translations = {
                k: translator.translate(v, dest='fa').text 
                for k, v in venue_city_translations.items()
            } if venue_city_translations else {}
            
            round_fa_translations = {
                k: translator.translate(str(k), dest='fa').text 
                for k in round_translations
            } if round_translations else {}
            
            # Create fixtures
            fixtures_to_create = []
            for fixture in fixtures_data:
                # Modify round name
                league_round = fixture['league']['round'] or 'Unknown Round'
                if isinstance(league_round, str) and 'Regular Season' in league_round:
                    league_round = league_round.replace('Regular Season', 'week')
                
                # Get home and away teams
                home_team = Team.objects.get(team_id=fixture['teams']['home']['id'])
                away_team = Team.objects.get(team_id=fixture['teams']['away']['id'])
                
                # Create fixture object
                fixture_obj = Fixture(
                    league_id=league_id,
                    season_id=Season.objects.get(league_id=league_id, year=season).id,
                    fixture_id=fixture['fixture']['id'],
                    fixture_referee=fixture['fixture']['referee'] or '',
                    fixture_faReferee=referee_fa_translations.get(fixture['fixture']['referee'], ''),
                    fixture_timestamp=fixture['fixture']['timestamp'],
                    fixture_periods_first=fixture['fixture']['periods']['first'],
                    fixture_periods_second=fixture['fixture']['periods']['second'],
                    fixture_venue_name=fixture['fixture']['venue']['name'] or '',
                    fixture_venue_faName=venue_name_fa_translations.get(fixture['fixture']['venue']['name'], ''),
                    fixture_venue_city=fixture['fixture']['venue']['city'] or '',
                    fixture_venue_faCity=venue_city_fa_translations.get(fixture['fixture']['venue']['city'], ''),
                    fixture_status_long=fixture['fixture']['status']['long'],
                    fixture_status_short=fixture['fixture']['status']['short'],
                    fixture_status_elapsed=fixture['fixture']['status']['elapsed'],
                    fixture_status_extra=fixture['fixture']['status']['extra'],
                    league_round=league_round,
                    teams_home=home_team,
                    teams_home_winner=fixture['teams']['home']['winner'],
                    teams_away=away_team,
                    teams_away_winner=fixture['teams']['away']['winner'],
                    goals=fixture['goals'],
                    score_halftime=fixture['score']['halftime'],
                    score_fulltime=fixture['score']['fulltime'],
                    score_extratime=fixture['score']['extratime'],
                    score_penalty=fixture['score']['penalty']
                )
                fixtures_to_create.append(fixture_obj)
            
            # Bulk create fixtures
            with transaction.atomic():
                Fixture.objects.bulk_create(fixtures_to_create)
                
                # Create or update FixtureRound
                FixtureRound.objects.update_or_create(
                    league_id=league_id,
                    season_id=Season.objects.get(league_id=league_id, year=season).id,
                    defaults={'rounds': round_fa_translations}
                )
            
            # Retrieve and serialize fixtures
            fixtures = Fixture.objects.filter(
                league_id=league_id, 
                season__year=season
            )
            serializer = FixtureSerializer(fixtures, many=True)
            
            return Response({
                'fixtures': serializer.data,
                'rounds': round_fa_translations
            })
        
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"API request failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def ensure_teams_exist(self, league_id, season, fixtures_data):
        # Collect unique team IDs
        team_ids = set()
        for fixture in fixtures_data:
            team_ids.add(fixture['teams']['home']['id'])
            team_ids.add(fixture['teams']['away']['id'])
        
        # Check which teams don't exist
        non_existent_teams = [
            team_id for team_id in team_ids 
            if not Team.objects.filter(team_id=team_id).exists()
        ]
        
        # If there are non-existent teams, fetch them
        if non_existent_teams:
            team_view = TeamView()
            team_view.get_teams_from_api(None, league_id, season)



class FixtureRoundView(APIView):
    def get(self, request, league, fixture_round, season=None):
        try:
            # If no season provided, use current year
            if season is None:
                season = str(get_year())
            
            # Check if league is supported
            league_id = myleague_ids.get(league)
            if league_id is None:
                return Response(
                    {"error": "Wrong League"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ensure league exists
            try:
                league_data = League.objects.get(league_id=league_id)
            except League.DoesNotExist:
                from .views import LeagueView
                league_response = LeagueView().fetch_league_data_from_api(league_id)
                if league_response.status_code != 200:
                    return league_response
                league_data = League.objects.get(league_id=league_id)
            
            # Ensure season exists
            try:
                season_data = Season.objects.get(league=league_data, year=season)
            except Season.DoesNotExist:
                return Response(
                    {"error": "Invalid season"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if FixtureRound exists for this league and season
            try:
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data, 
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds
            except FixtureRound.DoesNotExist:
                # If no fixture rounds exist, fetch fixtures from API
                fixture_view = FixtureView()
                fixture_response = fixture_view.get_fixtures_from_api(league_id, season)
                
                # If API fetch fails
                if not isinstance(fixture_response, Response) or fixture_response.status_code != 200:
                    return fixture_response
                
                # Retry getting fixture rounds
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data, 
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds
            
            # Check if the requested round exists in the rounds dictionary
            if fixture_round not in rounds_dict:
                return Response(
                    {"error": f"Round {fixture_round} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Retrieve fixtures for the specific round
            fixtures = Fixture.objects.filter(
                league=league_data, 
                season=season_data, 
                league_round=fixture_round
            )
            
            # If no fixtures found for the specific round
            if not fixtures.exists():
                return Response(
                    {"error": f"No fixtures found for round: {fixture_round}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Serialize and return fixtures
            serializer = FixtureSerializer(fixtures, many=True)
            
            return Response({
                'fixtures': serializer.data,
                'round': fixture_round
            })
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





class FixtureRoundFaView(APIView):
    def get(self, request, league, fixture_round_fa, season=None):
        try:
            # If no season provided, use current year
            if season is None:
                season = str(get_year())
            
            # Check if league is supported
            league_id = myleague_ids.get(league)
            if league_id is None:
                return Response(
                    {"error": "Wrong League"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ensure league exists
            try:
                league_data = League.objects.get(league_id=league_id)
            except League.DoesNotExist:
                from .views import LeagueView
                league_response = LeagueView().fetch_league_data_from_api(league_id)
                if league_response.status_code != 200:
                    return league_response
                league_data = League.objects.get(league_id=league_id)
            
            # Ensure season exists
            try:
                season_data = Season.objects.get(league=league_data, year=season)
            except Season.DoesNotExist:
                return Response(
                    {"error": "Invalid season"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if FixtureRound exists for this league and season
            try:
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data, 
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds
            except FixtureRound.DoesNotExist:
                # If no fixture rounds exist, fetch fixtures from API
                fixture_view = FixtureView()
                fixture_response = fixture_view.get_fixtures_from_api(league_id, season)
                
                # If API fetch fails
                if not isinstance(fixture_response, Response) or fixture_response.status_code != 200:
                    return fixture_response
                
                # Retry getting fixture rounds
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data, 
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds
            
            # Debugging output
            print("Rounds Dictionary:", rounds_dict)
            print("Looking for round:", fixture_round_fa)
            
            # Find the key corresponding to the provided Persian round name
            fixture_round_key = next((key for key, value in rounds_dict.items() if value == fixture_round_fa), None)
            
            if fixture_round_key is None:
                return Response(
                    {"error": f"Round '{fixture_round_fa}' not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Retrieve fixtures for the specific round
            fixtures = Fixture.objects.filter(
                league=league_data, 
                season=season_data, 
                league_round=fixture_round_key
            )
            
            # If no fixtures found for the specific round
            if not fixtures.exists():
                return Response(
                    {"error": f"No fixtures found for round: {fixture_round_key}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Serialize and return fixtures
            serializer = FixtureSerializer(fixtures, many=True)
            
            return Response({
                'fixtures': serializer.data,
                'round': fixture_round_key
            })
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    




class FixtureStatView(APIView):
    def get(self, request, fixture_id):
        logger.info(f"Received request for fixture_id: {fixture_id}")

        # Check if statistics already exist for this fixture
        fixture_stats = FixtureStat.objects.filter(fixture__fixture_id=fixture_id)

        if fixture_stats.exists():
            # If statistics exist, serialize and return them
            serializer = FixtureStatSerializer(fixture_stats, many=True)
            logger.info("Returning existing fixture statistics")
            return Response(serializer.data)

        logger.info("Fetching statistics from the API")
        # If statistics do not exist, fetch from the API
        return self.fetch_statistics_from_api(fixture_id)

    def fetch_statistics_from_api(self, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        headers = accheaders  # Ensure accheaders is defined with your API credentials

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json().get('response', [])

            # Prepare to save statistics
            fixture_stats_to_create = []
            for team_stats in data:
                team_id = team_stats['team']['id']
                
                # Create a new FixtureStat instance
                stats = team_stats['statistics']
                fixture_stat = FixtureStat(
                    fixture=Fixture.objects.get(fixture_id=fixture_id),  # Retrieve fixture here
                    team=Team.objects.get(team_id=team_id),
                    ShotsOnGoal=self.get_stat_value(stats, "Shots on Goal"),
                    ShotsOffGoal=self.get_stat_value(stats, "Shots off Goal"),
                    TotalShots=self.get_stat_value(stats, "Total Shots"),
                    BlockedShots=self.get_stat_value(stats, "Blocked Shots"),
                    ShotsInsideBox=self.get_stat_value(stats, "Shots insidebox"),
                    ShotsOutsideBox=self.get_stat_value(stats, "Shots outsidebox"),
                    Fouls=self.get_stat_value(stats, "Fouls"),
                    CornerKicks=self.get_stat_value(stats, "Corner Kicks"),
                    Offsides=self.get_stat_value(stats, "Offsides"),
                    BallPossession=self.get_stat_value(stats, "Ball Possession"),
                    YellowCards=self.get_stat_value(stats, "Yellow Cards"),
                    RedCards=self.get_stat_value(stats, "Red Cards"),
                    GoalkeeperSaves=self.get_stat_value(stats, "Goalkeeper Saves"),
                    Totalpasses=self.get_stat_value(stats, "Total passes"),
                    Passesaccurate=self.get_stat_value(stats, "Passes accurate"),
                    PassesPercent=self.get_stat_value(stats, "Passes %"),
                    ExpectedGoals=self.get_stat_value(stats, "expected_goals"),
                    GoalsPrevented=self.get_stat_value(stats, "goals_prevented"),
                )
                fixture_stats_to_create.append(fixture_stat)

            # Bulk create FixtureStat instances
            FixtureStat.objects.bulk_create(fixture_stats_to_create)

            # Return the newly created statistics
            serializer = FixtureStatSerializer(fixture_stats_to_create, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch fixture statistics: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_stat_value(self, stats, stat_type):
        """Helper method to get the value of a specific statistic type."""
        for stat in stats:
            if stat['type'] == stat_type:
                return stat['value']
        return None




class FixtureEventView(APIView):
    def get(self, request, fixture_id):
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        try:
            fixture_event_data = FixtureEvent.objects.filter(fixture=fixture_data)
            if fixture_event_data.exists():
                serializer = FixtureEventSerializer(fixture_event_data, many=True)
                return Response(serializer.data)
            else:
                return self.get_fixture_event_from_api(request, fixture_id, fixture_data)
        except FixtureEvent.DoesNotExist:
            return self.get_fixture_event_from_api(request, fixture_id, fixture_data)

    def get_fixture_event_from_api(self, request, fixture_id, fixture_data):
        url = f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            fixture_event_list = []
            for event_data in data['response']:
                team_obj = Team.objects.get(team_id=event_data['team']['id'])
                if 'player' in event_data and event_data['player'] and 'id' in event_data['player']:
                    try:
                        player_obj = Player.objects.get(player_id=event_data['player']['id'])
                    except Player.DoesNotExist:
                        player_obj = None
                else:
                    player_obj = None
                if 'assist' in event_data and event_data['assist'] and 'id' in event_data['assist']:
                    try:
                        assist_obj = Player.objects.get(player_id=event_data['assist']['id'])
                    except Player.DoesNotExist:
                        assist_obj = None
                else:
                    assist_obj = None
                fixture_event_dict = {
                    'fixture': fixture_data,
                    'team': team_obj,
                    'player': player_obj,
                    'assist': assist_obj,
                    'type': event_data['type'],
                    'detail': event_data['detail'],
                    'comments': event_data['comments'],
                    'time_elapsed': event_data['time']['elapsed'],
                    'time_extra': event_data['time']['extra'],
                }
                fixture_event_list.append(fixture_event_dict)

            FixtureEvent.objects.bulk_create([FixtureEvent(**fixture_event) for fixture_event in fixture_event_list])

            serializer = FixtureEventSerializer(FixtureEvent.objects.filter(fixture=fixture_data), many=True)
            return Response(serializer.data)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)






class FixtureLineupView(APIView):
    def get(self, request, fixture_id):
        # Step 1: Check if the fixture exists
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        # Step 2: Check if the lineup already exists
        fixture_lineup_data = FixtureLineup.objects.filter(fixture=fixture_data)
        if fixture_lineup_data.exists():
            serializer = FixtureLineupSerializer(fixture_lineup_data, many=True)
            return Response(serializer.data)
        else:
            return self.get_fixture_lineup_from_api(request, fixture_id, fixture_data)

    def get_fixture_lineup_from_api(self, request, fixture_id, fixture_data):
        url = f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            fixture_lineup_list = []

            for team_data in data['response']:
                team_obj = Team.objects.get(team_id=team_data['team']['id'])
                coach_id = team_data['coach']['id']

                # Step 3: Check if the coach exists, if not fetch from API
                if not Coach.objects.filter(coach_id=coach_id).exists():
                    CoachView().get_coaches_from_api(team_obj.team_id)

                # Fetch or create the coach
                coach_obj, _ = Coach.objects.get_or_create(
                    coach_id=coach_id,
                    defaults={
                        'name': team_data['coach']['name'],
                        'photo': team_data['coach']['photo'],
                        'team': team_obj,
                    }
                )

                # Step 4: Process players in startXI
                players_start_xi = self.process_players(team_data['startXI'], team_obj, fixture_data.league, fixture_data.season)
                
                # Step 5: Process substitutes
                players_substitutes = self.process_players(team_data['substitutes'], team_obj, fixture_data.league, fixture_data.season)

                # Create FixtureLineup instance
                fixture_lineup_instance = FixtureLineup(
                    fixture=fixture_data,
                    team=team_obj,
                    team_color=team_data['team']['colors'],
                    coach=coach_obj,
                    formation=team_data['formation'],
                )
                fixture_lineup_instance.save()

                # Add players to start_xi and substitutes
                fixture_lineup_instance.start_xi.set(players_start_xi)
                fixture_lineup_instance.substitutes.set(players_substitutes)

                fixture_lineup_list.append(fixture_lineup_instance)

            # Step 6: Return the fixture lineup data
            serializer = FixtureLineupSerializer(fixture_lineup_list, many=True)
            return Response(serializer.data)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)

    def process_players(self, players_data, team_obj, league, season):
        player_list = []
        for player_data in players_data:
            player_id = player_data['player']['id']

            # Step 7: Check if the player exists, if not use PlayerView to fetch
            if not Player.objects.filter(player_id=player_id).exists():
                PlayerView().get_players_from_api(None, league.league_id, team_obj.team_id, season.year, team_obj, season)

            # Fetch or create the player
            player_obj, _ = Player.objects.get_or_create(
                player_id=player_id,
                defaults={
                    'name': player_data['player']['name'],
                    'number': player_data['player']['number'],
                    'position': player_data['player']['pos'],
                    'team': team_obj,
                    'season': season,
                }
            )

            # Update existing player details if necessary
            player_obj.number = player_data['player']['number']
            player_obj.position = player_data['player']['pos']
            player_obj.save()

            # Add the player to the list
            player_list.append(player_obj)

        return player_list

class FixturePlayerView(APIView):
    def get(self, request, fixture_id):
        # Step 1: Check if the fixture exists
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Check if FixturePlayer data exists for this fixture
        fixture_players = FixturePlayer.objects.filter(fixture=fixture_data)

        if fixture_players.exists():
            # If statistics exist, serialize and return them
            serializer = FixturePlayerSerializer(fixture_players, many=True)
            return Response(serializer.data)

        # Step 3: If no FixturePlayer data exists, fetch from the API
        return self.fetch_players_from_api(fixture_id, fixture_data)

    def fetch_players_from_api(self, fixture_id, fixture_data):
        url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
        headers = accheaders  # Ensure accheaders is defined with your API credentials

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()['response']

            # Prepare to save statistics
            fixture_players_to_create = []
            for team_data in data:
                team_id = team_data['team']['id']
                team_obj = Team.objects.get(team_id=team_id)

                for player_data in team_data['players']:
                    player_id = player_data['player']['id']
                    player_obj = Player.objects.get(player_id=player_id)

                    # Extract statistics
                    statistics = player_data['statistics'][0]  # Assuming there's always at least one statistics entry
                    games = statistics['games']

                    fixture_player = FixturePlayer(
                        fixture=fixture_data,
                        team=team_obj,
                        player=player_obj,
                        minutes=games.get('minutes'),
                        rating=float(games.get('rating', 0.0)) if games.get('rating') is not None else 0.0,
                        captain=games.get('captain', False),
                        substitute=games.get('substitute', False),
                        shots_total=statistics['shots'].get('total'),
                        shots_on=statistics['shots'].get('on'),
                        goals_total=statistics['goals'].get('total'),
                        goals_conceded=statistics['goals'].get('conceded'),
                        assists=statistics['goals'].get('assists'),
                        saves=statistics['goals'].get('saves'),
                        passes_total=statistics['passes'].get('total'),
                        passes_key=statistics['passes'].get('key'),
                        passes_accuracy=statistics['passes'].get('accuracy'),
                        tackles_total=statistics['tackles'].get('total'),
                        blocks=statistics['tackles'].get('blocks'),
                        interceptions=statistics['tackles'].get('interceptions'),
                        duels_total=statistics['duels'].get('total'),
                        duels_won=statistics['duels'].get('won'),
                        dribbles_attempts=statistics['dribbles'].get('attempts'),
                        dribbles_success=statistics['dribbles'].get('success'),
                        dribbles_past=statistics['dribbles'].get('past'),
                        fouls_drawn=statistics['fouls'].get('drawn'),
                        fouls_committed=statistics['fouls'].get('committed'),
                        cards_yellow=statistics['cards'].get('yellow'),
                        cards_yellow_red=statistics['cards'].get('yellowred'),
                        cards_red=statistics['cards'].get('red'),
                        penalty_won=statistics['penalty'].get('won'),
                        penalty_commited=statistics['penalty'].get('commited'),
                        penalty_scored=statistics['penalty'].get('scored'),
                        penalty_missed=statistics['penalty'].get('missed'),
                        penalty_saved=statistics['penalty'].get('saved'),
                    )
                    fixture_players_to_create.append(fixture_player)

            # Bulk create FixturePlayer instances
            FixturePlayer.objects.bulk_create(fixture_players_to_create)

            # Return the newly created statistics
            serializer = FixturePlayerSerializer(fixture_players_to_create, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch fixture player data: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class FixtureH2H(APIView):
    def get(self, request, fixture_id):
        try:
            # Check if the fixture exists in the database
            fixture = Fixture.objects.get(fixture_id=fixture_id)
            home_team_id = fixture.teams_home.team_id
            away_team_id = fixture.teams_away.team_id
            
            # Fetch all fixtures with the same home or away teams and status "FT"
            fixtures = Fixture.objects.filter(
                (Q(teams_home_id=home_team_id) & Q(teams_away_id=away_team_id)) |
                (Q(teams_home_id=away_team_id) & Q(teams_away_id=home_team_id)),
                fixture_status_short="FT"  # Filter for fixtures with status "FT"
            ).order_by('-fixture_timestamp')  # Sort by timestamp descending

            if len(fixtures) < 3:  # Check if there are fewer than 3 fixtures
                return self.fetch_h2h_from_api(home_team_id, away_team_id)

            # Calculate summary
            final_summary, league_stats = self.calculate_summary(fixtures, fixture)

            # Serialize fixtures
            serializer = FixtureH2HSerializer(fixtures, many=True)

            # Combine summary and fixtures into one response
            response_data = {
                "summary": final_summary,
                "fixtures": serializer.data
            }

            return Response(response_data)

        except Fixture.DoesNotExist:
            return Response({"error": "Fixture does not exist"}, status=404)

    def fetch_h2h_from_api(self, home_team_id, away_team_id):
        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={home_team_id}-{away_team_id}"
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()['response']

            fixtures_list = []
            for fixture_data in data:
                league_id = fixture_data['league']['id']
                season_year = fixture_data['fixture']['date'][:4]  # Extract year from the fixture date

                # Check if league exists in the database
                league, created = League.objects.get_or_create(
                    league_id=league_id,
                    defaults={
                        'league_name': fixture_data['league']['name'],
                        'league_logo': fixture_data['league']['logo'],
                        'league_country': fixture_data['league']['country'],
                    }
                )

                # Check if season exists in the database
                season, created = Season.objects.get_or_create(
                    league=league,  # Associate with the league
                    year=season_year,
                )

                # Create or update fixture in the database
                fixture_obj, created = Fixture.objects.update_or_create(
                    fixture_id=fixture_data['fixture']['id'],
                    defaults={
                        'league': league,
                        'season': season,  # Ensure season is set here
                        'teams_home_id': fixture_data['teams']['home']['id'],
                        'teams_away_id': fixture_data['teams']['away']['id'],
                        'goals': fixture_data['goals'],
                        'score_halftime': fixture_data['score']['halftime'],
                        'score_fulltime': fixture_data['score']['fulltime'],
                        'score_extratime': fixture_data['score']['extratime'],
                        'score_penalty': fixture_data['score']['penalty'],
                        'fixture_referee': fixture_data['fixture']['referee'],
                        'fixture_timestamp': fixture_data['fixture']['timestamp'],
                        'fixture_periods_first': fixture_data['fixture']['periods']['first'],
                        'fixture_periods_second': fixture_data['fixture']['periods']['second'],
                        'fixture_venue_name': fixture_data['fixture']['venue']['name'],
                        'fixture_venue_city': fixture_data['fixture']['venue']['city'],
                        'fixture_status_long': fixture_data['fixture']['status']['long'],
                        'fixture_status_short': fixture_data['fixture']['status']['short'],
                        'fixture_status_elapsed': fixture_data['fixture']['status']['elapsed'],
                    }
                )

                fixtures_list.append(fixture_obj)

            # Sort fixtures by timestamp in descending order before serialization
            fixtures_list.sort(key=lambda x: x.fixture_timestamp, reverse=True)

            # Calculate summary for fetched fixtures
            final_summary, league_stats = self.calculate_summary(fixtures_list, fixtures_list[0])

            serializer = FixtureH2HSerializer(fixtures_list, many=True)
            response_data = {
                "summary": final_summary,
                "fixtures": serializer.data
            }

            return Response(response_data)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch head-to-head data: " + str(e)}, status=500)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=500)

    def calculate_summary(self, fixtures, fixture):
        # Initialize summary
        summary = {
            "total_fixtures": len(fixtures),
            "total_goals": 0,
            "draws": 0,
            f"{fixture.teams_home.team_name} goals": 0,
            f"{fixture.teams_away.team_name} goals": 0,
            f"{fixture.teams_home.team_name} wins": 0,
            f"{fixture.teams_away.team_name} wins": 0,
        }

        # Initialize league-specific statistics
        league_stats = {}

        # Iterate over each fixture to calculate statistics
        for fixture in fixtures:
            home_goals = fixture.score_fulltime.get('home', 0) or 0
            away_goals = fixture.score_fulltime.get('away', 0) or 0

            # Update total goals
            summary["total_goals"] += home_goals + away_goals

            # Update home and away goals
            summary[f"{fixture.teams_home.team_name} goals"] += home_goals
            summary[f"{fixture.teams_away.team_name} goals"] += away_goals

            # Determine wins and draws
            if home_goals > away_goals:
                summary[f"{fixture.teams_home.team_name} wins"] += 1
            elif away_goals > home_goals:
                summary[f"{fixture.teams_away.team_name} wins"] += 1
            else:
                summary["draws"] += 1

            # Initialize league entry if not already present
            league_name = fixture.league.league_name
            if league_name not in league_stats:
                league_stats[league_name] = {
                    "total_fixtures": 0,
                    "total_goals": 0,
                    f"{fixture.teams_home.team_name} goals": 0,
                    f"{fixture.teams_away.team_name} goals": 0,
                    f"{fixture.teams_home.team_name} wins": 0,
                    f"{fixture.teams_away.team_name} wins": 0,
                    "draws": 0,
                }

            # Update league statistics
            league_stats[league_name]["total_fixtures"] += 1
            league_stats[league_name]["total_goals"] += home_goals + away_goals
            league_stats[league_name][f"{fixture.teams_home.team_name} goals"] += home_goals
            league_stats[league_name][f"{fixture.teams_away.team_name} goals"] += away_goals

            if home_goals > away_goals:
                league_stats[league_name ][f"{fixture.teams_home.team_name} wins"] += 1
            elif away_goals > home_goals:
                league_stats[league_name][f"{fixture.teams_away.team_name} wins"] += 1
            else:
                league_stats[league_name]["draws"] += 1

        # Create the final summary dictionary
        final_summary = {
            "total_fixtures": summary["total_fixtures"],
            "total_goals": summary["total_goals"],
            "draws": summary["draws"],
            f"{fixture.teams_home.team_name} goals": summary[f"{fixture.teams_home.team_name} goals"],
            f"{fixture.teams_away.team_name} goals": summary[f"{fixture.teams_away.team_name} goals"],
            f"{fixture.teams_home.team_name} wins": summary[f"{fixture.teams_home.team_name} wins"],
            f"{fixture.teams_away.team_name} wins": summary[f"{fixture.teams_away.team_name} wins"],
        }

        # Add league-specific statistics to the final summary
        for league_name, stats in league_stats.items():
            final_summary[league_name] = {
                "total_fixtures": stats["total_fixtures"],
                "total_goals": stats["total_goals"],
                f"{fixture.teams_home.team_name} goals": stats[f"{fixture.teams_home.team_name} goals"],
                f"{fixture.teams_away.team_name} goals": stats[f"{fixture.teams_away.team_name} goals"],
                f"{fixture.teams_home.team_name} wins": stats[f"{fixture.teams_home.team_name} wins"],
                f"{fixture.teams_away.team_name} wins": stats[f"{fixture.teams_away.team_name} wins"],
                "draws": stats ["draws"],
            }

        return final_summary, league_stats




# class FixtureDateView(APIView):
#     def get(self, request, date=None):
#         if date is None:
#             date = get_today_date()  # Get today's date if no date is provided

#         # Convert date to timestamp and add 86400 seconds (24 hours)
#         start_timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
#         end_timestamp = start_timestamp + 86400

#         # Fetch fixtures between the two timestamps from the Fixture model
#         fixtures = Fixture.objects.filter(fixture_timestamp__gte=start_timestamp, fixture_timestamp__lt=end_timestamp)
#         if fixtures.exists():
#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response(serializer.data)
#         else:
#             return self.fetch_fixtures_date(request, date)

#     def fetch_fixtures_date(self, request, date):
#         url = f"https://v3.football.api-sports.io/fixtures?date={date}"
#         headers = accheaders  # Ensure accheaders is defined
        
#         try:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
#             fixtures_data = response.json()['response']
            
#             translator = Translator()
#             for fixture_data in fixtures_data:
#                 league_id = fixture_data['league']['id']

#                 # Check if league_id exists in myleague_ids
#                 if league_id not in myleague_ids.values():
#                     continue  # Skip if league_id is not in myleague_ids

#                 # Check if league_id exists in Leagues model
#                 if not League.objects.filter(league_id=league_id).exists():
#                     # If league_id does not exist, fetch league data from API
#                     LeagueView().fetch_league_data_from_api(league_id)  # Pass league_id correctly

#                 # Fetch the league instance
#                 league_instance = League.objects.get(league_id=league_id)

#                 # Get the season from the fixture data
#                 season_year = fixture_data['league']['season']

#                 # Fetch or create the Season instance, ensuring unique entries
#                 season_instance, created = Season.objects.get_or_create(year=season_year)

#                 # Extract teams' IDs
#                 home_team_id = fixture_data['teams']['home']['id']
#                 away_team_id = fixture_data['teams']['away']['id']
#                 venue_data = fixture_data['fixture']['venue']

#                 # Check if venue data is available
#                 venue_info = {
#                     'id': venue_data.get('id'),
#                     'name': venue_data.get('name'),
#                     'city': venue_data.get('city'),
#                     'faName': translator.translate(venue_data.get('name', ''), dest='fa').text if venue_data.get('name') else None,
#                     'faCity': translator.translate(venue_data.get('city', ''), dest='fa').text if venue_data.get('city') else None,
#                 }

#                 # Check if home or away team exists in Team
#                 home_team_exists = Team.objects.filter(team_id=home_team_id).exists()
#                 away_team_exists = Team.objects.filter(team_id=away_team_id).exists()

#                 # If either team does not exist, fetch the teams from the API
#                 if not home_team_exists or not away_team_exists:
#                     TeamView().get_teams_from_api(request, league_id, season_year)

#                 # Now that teams are ensured to exist, save the fixture in the database
#                 fixture_obj, created = Fixture.objects.update_or_create(
#                     fixture_id=fixture_data['fixture']['id'],
#                     defaults={
#                         'league': league_instance,  # Use the league instance here
#                         'season': season_instance,   # Use the season instance here
#                         'teams_home': home_team_id,
#                         'teams_away': away_team_id,
#                         'fixture_referee': fixture_data['fixture']['referee'],
#                         'fixture_timestamp': fixture_data['fixture']['timestamp'],
#                         'fixture_periods_first': fixture_data['fixture']['periods'].get('first'),
#                         'fixture_periods_second': fixture_data['fixture']['periods'].get('second'),
#                         'fixture_venue_name': venue_data['name'],
#                         'fixture_venue_faName': venue_info['faName'],
#                         'fixture_venue_city': venue_data['city'],
#                         'fixture_venue_faCity': venue_info['faCity'],
#                         'fixture_status_long': fixture_data['fixture']['status']['long'],
#                         'fixture_status_short': fixture_data['fixture']['status']['short'],
#                         'fixture_status_elapsed': fixture_data['fixture']['status']['elapsed'],
#                         'goals': fixture_data['goals'],
#                         'score_halftime': fixture_data['score'].get('halftime'),
#                         'score_fulltime': fixture_data['score'].get('fulltime'),
#                         'score_extratime': fixture_data['score'].get('extratime'),
#                         'score_penalty': fixture_data['score'].get('penalty'),
#                     }
#                 )

#             # After saving all fixtures, return the fixtures from the database
#             fixtures = Fixture.objects.filter(fixture_timestamp__gte=int(datetime.strptime(date, "%Y-%m-%d").timestamp()),
#                                                fixture_timestamp__lt=int(datetime.strptime(date, "%Y-%m-%d").timestamp() + 86400))
#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response(serializer.data)
#         except requests.exceptions.RequestException as e:
#             return Response({"error": "Failed to fetch fixtures from API: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FixtureDateView(APIView):
    def get(self, request, date=None):
        if date is None:
            date = get_today_date()  # Get today's date if no date is provided

        # Convert date to timestamp and add 86400 seconds (24 hours)
        start_timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        end_timestamp = start_timestamp + 86400

        # Fetch fixtures between the two timestamps from the Fixture model
        fixtures = Fixture.objects.filter(fixture_timestamp__gte=start_timestamp, fixture_timestamp__lt=end_timestamp)
        if fixtures.exists():
            serializer = FixtureSerializer(fixtures, many=True)
            return Response(serializer.data)
        else:
            return self.fetch_fixtures_date(request, date)

    def fetch_fixtures_date(self, request, date):
        url = f"https://v3.football.api-sports.io/fixtures?date={date}"
        headers = accheaders  # Ensure accheaders is defined
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            fixtures_data = response.json()['response']
            
            translator = Translator()
            for fixture_data in fixtures_data:
                league_id = fixture_data['league']['id']

                # Check if league_id exists in myleague_ids
                if league_id not in myleague_ids.values():
                    continue  # Skip if league_id is not in myleague_ids

                # Ensure league exists
                league_instance = self.get_or_create_league(league_id)

                # Get the season from the fixture data
                season_year = fixture_data['league']['season']
                season_instance, _ = Season.objects.get_or_create(year=season_year)

                # Extract teams' IDs
                home_team_id = fixture_data['teams']['home']['id']
                away_team_id = fixture_data['teams']['away']['id']
                venue_data = fixture_data['fixture']['venue']

                # Check if venue data is available
                venue_info = {
                    'id': venue_data.get('id'),
                    'name': venue_data.get('name'),
                    'city': venue_data.get('city'),
                    'faName': translator.translate(venue_data.get('name', ''), dest='fa').text if venue_data.get('name') else None,
                    'faCity': translator.translate(venue_data.get('city', ''), dest='fa').text if venue_data.get('city') else None,
                }

                # Ensure teams exist
                self.ensure_teams_exist(home_team_id, away_team_id, league_id, season_year)

                # Create or update the fixture
                fixture_obj, _ = Fixture.objects.update_or_create(
                    fixture_id=fixture_data['fixture']['id'],
                    defaults={
                        'league': league_instance,
                        'season': season_instance,
                        'teams_home': home_team_id,
                        'teams_away': away_team_id,
                        'fixture_referee': fixture_data['fixture']['referee'],
                        'fixture_timestamp': fixture_data['fixture']['timestamp'],
                        'fixture_periods_first': fixture_data['fixture']['periods'].get('first'),
                        'fixture_periods_second': fixture_data['fixture']['periods'].get('second'),
                        'fixture_venue_name': venue_data['name'] or '',
                        'fixture_venue_faName': venue_info['faName'],
                        'fixture_venue_city': venue_data['city'] or '',
                        'fixture_venue_faCity': venue_info['faCity'],
                        'fixture_status_long': fixture_data['fixture']['status']['long'],
                        'fixture_status_short': fixture_data['fixture']['status']['short'],
                        'fixture_status_elapsed': fixture_data['fixture']['status']['elapsed'],
                        'goals': fixture_data['goals'],
                        'score_halftime': fixture_data['score'].get('halftime'),
                        'score_fulltime': fixture_data['score'].get('fulltime'),
                        'score_extratime': fixture_data['score'].get('extratime'),
                        'score_penalty': fixture_data['score'].get('penalty'),
                    }
                )

            # After saving all fixtures, return the fixtures from the database
            fixtures = Fixture.objects.filter(fixture_timestamp__gte=int(datetime.strptime(date, "%Y-%m-%d").timestamp()),
                                               fixture_timestamp__lt=int(datetime.strptime(date, "%Y-%m-%d").timestamp() + 86400))
            serializer = FixtureSerializer(fixtures, many=True)
            return Response(serializer.data)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch fixtures from API: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_or_create_league(self, league_id):
        """Fetch or create the league instance."""
        try:
            return League.objects.get(league_id=league_id)
        except League.DoesNotExist:
            league_response = LeagueView().fetch_league_data_from_api(league_id)
            if league_response.status_code != 200:
                raise Exception("Failed to fetch league data")
            return League.objects.get(league_id=league_id)  # Return the newly created league

    def ensure_teams_exist(self, home_team_id, away_team_id, league_id, season_year):
        """Check if teams exist and fetch them from API if not."""
        team_ids = {home_team_id, away_team_id}
        for team_id in team_ids:
            if not Team.objects.filter(team_id=team_id).exists():
                TeamView().get_teams_from_api(None, league_id, season_year)