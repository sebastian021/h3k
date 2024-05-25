from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Match, MatchStats, MatchesEvents, MatchesLineUps, MatchesPlayerStats
from .serializers import MatchSerializer, MatchStatsSerializer, MatchEventsSerializer, MatchesLineUpSerializers, MatchPlayerStatSerializers
import requests
import re
import json
from fixtures.lastseason import get_today_date


class MatchesAPIView(APIView):
    def get(self, request, date=None):
        desired_league_ids = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11,
                              12, 13, 15, 16, 17, 18, 19, 20,
                              21, 22, 23, 24, 25, 26, 27, 28,
                              29, 30, 31, 32, 33, 34, 35, 36,
                              37, 39, 45, 46, 48, 61, 65, 66,
                              71, 73, 78, 81, 88, 90, 94, 96,
                              98, 101, 102, 128, 130, 135, 137,
                              140, 143, 203, 206, 253, 257, 290,
                              291, 292, 294, 301, 302, 305, 307,
                              480, 482, 483, 495, 504, 528, 529,
                              531, 532, 533, 541, 543, 547, 548,
                              550, 551, 556, 803, 804, 808, 810,
                              826, 896, 905, 1089, 1105,
                            ]

        # If date is not provided, use today's date
        if date is None:
            date_str = get_today_date()
        else:
            # Use regex to extract the date from the URL
            pattern = r'\d{4}-\d{2}-\d{2}'
            match = re.search(pattern, date)
            if match:
                date_str = match.group(0)
            else:
                return Response({'error': 'Invalid date format.'}, status=400)

        # Make a request to the API with the date as a parameter
        url = 'https://v3.football.api-sports.io/fixtures'
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        params = {'date': date_str}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        # Process the data and filter by league id
        matches = data['response']
        filtered_matches = [] 
        for match in matches: 
            if match['league']['id'] in desired_league_ids: 
                # Get or create a Match instance with the desired match data 
                selected_match_data = { 
                    'fixture_id' : match['fixture']['id'],
                    'match_date' : match['fixture']['date'],
                    'match_timestamp': match['fixture']['timestamp'],
                    'match_periods_first': match['fixture']['periods']['first'],
                    'match_periods_second' : match['fixture']['periods']['second'],
                    'match_venue_name' : match['fixture']['venue']['name'],
                    'match_venue_city' : match['fixture']['venue']['city'],
                    'match_status_long' : match['fixture']['status']['long'],
                    'league_id': match['league']['id'],
                    'league_name' : match['league']['name'],
                    'league_country' : match['league']['country'],
                    'league_logo' : match['league']['logo'],
                    'league_flag' : match['league']['flag'],
                    'league_season' : match['league']['season'],
                    'league_round' : match['league']['round'],
                    'home_team_name' : match['teams']['home']['name'],
                    'home_team_logo' : match['teams']['home']['logo'],
                    'home_team_winner': match['teams']['home']['winner'],
                    'away_team_name' : match['teams']['away']['name'],
                    'away_team_logo' : match['teams']['away']['logo'],
                    'away_team_winner': match['teams']['away']['winner'],
                    'home_team_goals' : match['goals']['home'],
                    'away_team_goals' : match['goals']['away'],
                    'halftime_score' : match['score']['halftime'],
                    'fulltime_score' : match['score']['fulltime'],
                    'match_refree' : match['fixture']['referee']   # Add other fields accordingly 
                } 
                match_instance, created = Match.objects.get_or_create(
                    match_date=selected_match_data['match_date'],
                    home_team_name=selected_match_data['home_team_name'],
                    away_team_name=selected_match_data['away_team_name'],
                    defaults=selected_match_data
                )

                if not created:
                    # Update the existing match instance with the new data
                    for key, value in selected_match_data.items():
                        setattr(match_instance, key, value)
                    match_instance.save()
                filtered_matches.append(selected_match_data) 
        # Serialize the filtered matches and return a JSON response 
        serializer = MatchSerializer(filtered_matches, many=True)
        return Response(serializer.data)


class MatchStatisticsView(APIView):
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
            fixture = Match.objects.get(fixture_id=fixture_id)

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
                fixture_stats = MatchStats.objects.create(
                    fixture_id=fixture,
                    statistics_data=team_stats_dict
                 # Store the stats dictionary
                )
                serializer = MatchStatsSerializer(fixture_stats)
                serialized_data.append(serializer.data)

                
            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch statistics data"}, 
                            status=response.status_code)

class MatchEventsView(APIView):
    def get(self, request, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            events_data = response.json()['response']
            fixture = Match.objects.get(fixture_id=fixture_id)

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
                

                event_stats = MatchesEvents.objects.create(
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

                serializer = MatchEventsSerializer(event_stats)
                serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)


class MatchesLineUpView(APIView):
    def get(self, request, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            lineup_data = response.json()['response']
            fixture = Match.objects.get(fixture_id=fixture_id)

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
                

                lineup = MatchesLineUps.objects.create(
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

                serializer = MatchesLineUpSerializers(lineup)
                serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)


class MatchesPlayersStatsView(APIView):
    def get(self, request, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            player_stats = response.json()['response']
            fixture = Match.objects.get(fixture_id=fixture_id)

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


                    player = MatchesPlayerStats.objects.create(
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
                    serializer = MatchPlayerStatSerializers(player)
                    serialized_data.append(serializer.data)

            return Response(serialized_data)
        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)