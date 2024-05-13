from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Fixtures, FixtureStats, FixturesEvents
from django.core.exceptions import ObjectDoesNotExist
from .serializers import FixturesSerializer, FixtureStatsSerializer, FixturesEventsSerializers
class FixturesAPIView(APIView):
    def get(self, request, year, league, round):
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
        
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        round_param = f"Regular Season - {round}"
        params = {
            'season': year,
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

                event_stats = FixturesEvents.objects.create(
                    fixture_id=fixture,
                    time=time_data,
                    team_id=team_id,
                    team_name=team_name,
                    logo=logo,
                    player_id=player_id,
                    player_name=player_name
                )

                serializer = FixturesEventsSerializers(event_stats)
                serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)