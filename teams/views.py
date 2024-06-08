from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import TeamInformation, TeamStatistics
from fixtures.lastseason import get_year
from .serializers import TeamInformationSerializers, TeamStatisticSerializers, PlayersInformationSerializers
# Create your views here.

class TeamInformationView(APIView):
    def get(self, request, league, season=None):
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
        
        url = f'https://v3.football.api-sports.io/teams?league={league_id}&season={season}'
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            league_id = response.json()['parameters']['league']
            season = response.json()['parameters']['season']
            data = response.json()['response']
            serialized_data = []  # Initialize serialized_data as an empty list
            for informations in data:
                league_id = league_id
                season = season
                team = informations['team']
                venue = informations['venue']
                team_info = TeamInformation.objects.create(
                    league_id = league_id,
                    season = season,
                    team=team,
                    venue=venue,                )
                serializer = TeamInformationSerializers(team_info)
                serialized_data.append(serializer.data)

            return Response(serialized_data)

        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)

class TeamStatisticView(APIView):
    def get(self, request, league, season=None, team_id=None):
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
        
        # Fetch team information based on team_id and season
        team_info = TeamInformation.objects.filter(season=season, team__id=team_id, league_id=league_id).first()
        if not team_info:
            return Response({"error": "Team not found"}, status=404)

        # Construct the API request URL
        url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={team_id}"

        # Set the API request headers
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }

        # Make the API request
        response = requests.get(url, headers=headers)

        # Check the API response status code
        if response.status_code == 200:
            data = response.json()['response']
            serialized_data = []  # Initialize serialized_data as an empty list
            for stats in data:
                team = data['team']
                league = data['league']
                form = data['form']
                fixtures = data['fixtures']
                goals = data['goals']
                biggest = data['biggest']
                clean_sheet = data['clean_sheet']
                failed_to_score = data['failed_to_score']
                penalty = data['penalty']
                lineups = data['lineups']
                cards = data['cards']

                team_stats = TeamStatistics.objects.create(
                    team = team,
                    league = league,
                    form = form,
                    fixtures = fixtures,
                    goals = goals,
                    biggest = biggest,
                    clean_sheet = clean_sheet,
                    failed_to_score = failed_to_score,
                    penalty = penalty,
                    lineups = lineups,
                    cards = cards,
                    )
                serializer = TeamStatisticSerializers(team_stats)
                serialized_data.append(serializer.data)

            return Response(serialized_data)

        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)


class PlayersView(APIView):
    def get(self, request, league, team_id, season=None):
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

        # Fetch team information based on team_id and season
        team_info = TeamInformation.objects.filter(season=season, team_id=team_id, league_id=league_id).first()
        if not team_info:
            return Response({"error": "Team not found"}, status=404)

        # Construct the API request URL
        url = f"https://v3.football.api-sports.io/players?league={league_id}&season={season}&team={team_id}"

        # Set the API request headers
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }

        # Make the API request
        response = requests.get(url, headers=headers)

        # Check the API response status code
        if response.status_code == 200:
            data = response.json()['response']
            total_pages = response.json()['paging']['total']

            # Loop through each page to get all players
            for page in range(1, total_pages + 1):
                page_url = f"{url}&page={page}"
                page_response = requests.get(page_url, headers=headers)
                page_data = page_response.json()['response']

                # Loop through each player in the page
                for player_data in page_data:
                    player = player_data['player']
                    player_stats = player_data['statistics'][0]

                    # Check if a PlayersInformation object already exists for this player and season
                    player_info, created = PlayersInformation.objects.get_or_create(
                        team_id=team_info,
                        season=season,
                        player=player,
                        defaults={
                            'player': player_data['player'],
                            'statistics': player_stats
                        }
                    )

                    # If a new object was created, update its statistics
                    if created:
                        player_info.player = player_data['player']
                        player_info.statistics = player_stats
                        player_info.save()

            # Return all PlayersInformation objects for this team and season
            player_infos = PlayersInformation.objects.filter(team_id=team_info, season=season)
            serialized_data = PlayersInformationSerializers(player_infos, many=True).data
            return Response(serialized_data)

        else:
            return Response({"error": "Failed to fetch player data"}, status=response.status_code)