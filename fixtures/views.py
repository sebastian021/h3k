from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Fixtures, FixtureStats, FixturesEvents, FixturesLineUps, FixturesPlayerStats
from django.core.exceptions import ObjectDoesNotExist
from .serializers import FixturesSerializer, FixtureStatsSerializer, FixturesEventsSerializers, FixturesLineUpSerializers, FixturesPlayerStatSerializers
import json
from fixtures.lastseason import get_year

class FixturesAPIView(APIView):
    def get(self, request, round, league, season=None):
        desired_league_ids = {
            'PremierLeague': 39,
            'Bundesliga': 78,
            'Laliga': 140,
            'SerieA': 135,
            'Ligue1': 61
        }
        
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league"}, status=400)
        if not season:
            # Default to current season
            season = get_year()
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        round_param = f"Regular Season - {round}"
        params = {
            'season': season,
            'round': round_param,
            'league': league_id
        }
        
        response = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params=params)
        data = response.json()['response']
        
        for fixture_data in data:
            fixture = Fixtures.objects.update_or_create(
                fixture_id=fixture_data['fixture']['id'],
                defaults={
                    'league_id': fixture_data['league']['id'],
                    'league_name': fixture_data['league']['name'],
                    'league_country': fixture_data['league']['country'],
                    'league_logo': fixture_data['league']['logo'],
                    'league_flag': fixture_data['league']['flag'],
                    'league_season': fixture_data['league']['season'],
                    'league_round': fixture_data['league']['round'],
                    'fixture_timestamp': fixture_data['fixture']['timestamp'],
                    'fixture_referee': fixture_data['fixture']['referee'],
                    'fixture_venue_name': fixture_data['fixture']['venue']['name'],
                    'fixture_venue_city': fixture_data['fixture']['venue']['city'],
                    'fixture_status_long': fixture_data['fixture']['status']['long'],
                    'fixture_status_short': fixture_data['fixture']['status']['short'],
                    'teams_home_name': fixture_data['teams']['home']['name'],
                    'teams_home_id': fixture_data['teams']['home']['id'],
                    'teams_home_logo': fixture_data['teams']['home']['logo'],
                    'teams_home_winner': str(fixture_data['teams']['home']['winner']),
                    'teams_away_name': fixture_data['teams']['away']['name'],
                    'teams_away_id': fixture_data['teams']['away']['id'],
                    'teams_away_logo': fixture_data['teams']['away']['logo'],
                    'teams_away_winner': str(fixture_data['teams']['away']['winner']),
                    'goals': str(fixture_data['goals']),
                    'score_halftime': str(fixture_data['score']['halftime']),
                    'score_fulltime': str(fixture_data['score']['fulltime']),
                    'score_extratime': str(fixture_data['score']['extratime']),
                    'score_penalty': str(fixture_data['score']['penalty'])
                }
            )
        
        return Response(data)

class FixtureStatistics(APIView):
    def get(self, request, fixture_id):
        # Fetch statistics data from API
        url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            statistics_data = response.json()['response']
            fixture = Fixtures.objects.get(fixture_id=fixture_id)

            # Create FixtureStats objects and serialize data
            serialized_data = []
            for team_stats in statistics_data:
                team_data = team_stats['team']
                stats_list = team_stats['statistics']

                # Create a dictionary to hold all statistics for the team
                team_stats_dict = {
                    'team_id': team_data['id'],
                    'team_name': team_data['name'],
                    'team_logo': team_data['logo'],
                    'statistics': stats_list  # Include the entire stats list
                }

                # Create FixtureStats object and serialize
                fixture_stats = FixtureStats.objects.create(
                    fixture_id=fixture,
                    statistics_data=team_stats_dict
                 # Store the stats dictionary
                )
                serializer = FixtureStatsSerializer(fixture_stats)
                serialized_data.append(serializer.data)

                
            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch statistics data"}, 
                            status=response.status_code)



class FixtureEvents(APIView):
    def get(self, request, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            events_data = response.json()['response']
            fixture = Fixtures.objects.get(fixture_id=fixture_id)

            serialized_data = []
            for event in events_data:
                time_data = event['time']
                team_id = event['team']['id']
                team_name = event['team']['name']
                logo = event['team']['logo']
                player_id = event['player']['id']
                player_name = event['player']['name']
                assist_id = event['assist']
                assist_name = event['assist']['name']
                type = event['type']
                detail = event['detail']
                comments = event['comments']
                

                event_stats = FixturesEvents.objects.create(
                    fixture_id=fixture,
                    time=time_data,
                    team_id=team_id,
                    team_name=team_name,
                    logo=logo,
                    player_id=player_id,
                    player_name=player_name,
                    assist_id = assist_id,
                    assist_name = assist_name,
                    type = type,
                    detail = detail,
                    comments = comments,

                )

                serializer = FixturesEventsSerializers(event_stats)
                serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)
        



class FixturesLineUpView(APIView):
    def get(self, request, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            lineup_data = response.json()['response']
            fixture = Fixtures.objects.get(fixture_id=fixture_id)

            serialized_data = []
            for lineup in lineup_data:
                team_id = lineup['team']['id']
                team_name = lineup['team']['name']
                logo = lineup['team']['logo']
                team_color = lineup['team']['colors']
                coach_id = lineup['coach']['id']
                coach_name = lineup['coach']['name']
                coach_photo = lineup['coach']['photo']
                formation = lineup['formation']
                startXI = lineup['startXI']
                substitutes = lineup['substitutes']
                

                lineup = FixturesLineUps.objects.create(
                    fixture_id=fixture,
                    team_id=team_id,
                    team_name=team_name,
                    logo=logo,
                    team_color=team_color,
                    coach_id = coach_id,
                    coach_name = coach_name,
                    coach_photo = coach_photo,
                    formation = formation,
                    startXI = startXI,
                    substitutes = substitutes

                )

                serializer = FixturesLineUpSerializers(lineup)
                serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)



class FixturesPlayersStatsView(APIView):
    def get(self, request, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            player_stats = response.json()['response']
            fixture = Fixtures.objects.get(fixture_id=fixture_id)

            serialized_data = []
            for stats in player_stats:
                team_id = stats['team']['id']
                team_name = stats['team']['name']
                logo = stats['team']['logo']
                update = stats['team']['update']
                for player_info in stats['players']:
                    player_id = player_info['player']['id']
                    player_name = player_info['player']['name']
                    player_photo = player_info['player']['photo']
                    player_statistics = player_info['statistics']


                    player = FixturesPlayerStats.objects.create(
                        fixture_id=fixture,
                        team_id=team_id,
                        team_name=team_name,
                        logo=logo,
                        update=update,
                        player_id=player_id,
                        player_name=player_name,
                        player_photo=player_photo,
                        player_statistics=json.dumps(player_statistics),
                    )
                    serializer = FixturesPlayerStatSerializers(player)
                    serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)