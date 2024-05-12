from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Match, MatchStats
from .serializers import MatchSerializer, MatchStatsSerializer
import requests
import re



class MatchesAPIView(APIView):
    def get(self, request, date):
        desired_league_ids = [1, 2, 3, 4, 6, 7, 9, 15, 16, 17, 19, 23, 25, 137, 290, 301, 10, 18, 504, 5, 143, 
                            21, 29, 30, 482, 31, 32, 33, 34, 37, 39, 45, 46, 48, 61, 78, 135, 140, 203, 495,
                            528, 529, 531, 547, 556, 803, 804, 808, 
                        ]

        # Use regex to extract the date from the URL
        pattern = r'\d{4}-\d{2}-\d{2}'
        match = re.search(pattern, date)
        if match:
            # Extract the date from the match object
            date_str = match.group(0)
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
