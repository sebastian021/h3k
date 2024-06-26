from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Teams, TeamInformation, TeamStatistics, PlayersInformation
from fixtures.lastseason import get_year
from .serializers import TeamsSerializers, TeamInformationSerializers, TeamStatisticSerializers, PlayersInformationSerializers
# Create your views here.
class TeamsView(APIView):
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
            teams = response.json()['response']
            serialized_data = []  # Initialize serialized_data as an empty list
            for team in teams:
                team_id = team['team']['id']
                team_name = team['team']['name']
                team_logo = team['team']['logo']
                # Try to get an existing TeamInformation instance
                try:
                    league_teams = Teams.objects.get(
                        team_id=team_id,
                        team_name=team_name,
                        team_logo=team_logo,
                    )
                except Teams.DoesNotExist:
                    # Create a new TeamInformation instance if it doesn't exist
                    league_teams = Teams.objects.create(
                        team_id=team_id,
                        team_name=team['team']['name'],
                        team_logo=team['team']['logo'],
                    )
                else:
                    # Update the existing instance
                    league_teams.team_id = team['team']['id']
                    league_teams.team_name = team['team']['name']
                    league_teams.team_logo = team['team']['logo']
                    league_teams.save()

                serializer = TeamsSerializers(league_teams)
                serialized_data.append(serializer.data)

            return Response(serialized_data)

        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)
        

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
            data = response.json()['response']
            serialized_data = []  # Initialize serialized_data as an empty list
            for informations in data:
                team_id = informations['team']['id']
                team_name = informations['team']['name']
                team_logo=informations['team']['logo']
                # Try to get an existing Teams instance
                try:
                    team = Teams.objects.get(
                        team_id=team_id,
                        team_name=team_name,
                        team_logo=team_logo
                    )
                except Teams.DoesNotExist:
                    # Create a new Teams instance if it doesn't exist
                    team = Teams.objects.create(
                        team_id=team_id,
                        team_name=team_name,
                        team_logo=team_logo
                    )
                # Try to get an existing TeamInformation instance
                try:
                    team_info = TeamInformation.objects.get(
                        team=team
                    )
                except TeamInformation.DoesNotExist:
                    # Create a new TeamInformation instance if it doesn't exist
                    team_info = TeamInformation.objects.create(
                        team=team,
                        team_code=informations['team']['code'],
                        team_country=informations['team']['country'],
                        team_founded=informations['team']['founded'],
                        team_national=informations['team']['national'],
                        venue=informations['venue']
                    )
                else:
                    # Update the existing instance
                    team_info.team_code = informations['team']['code']
                    team_info.team_country = informations['team']['country']
                    team_info.team_founded = informations['team']['founded']
                    team_info.team_national = informations['team']['national']
                    team_info.venue = informations['venue']
                    team_info.save()

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

        # Try to get the team statistics from the database
        team_stats = TeamStatistics.objects.filter(team_id=team_id, season=season).first()
        if team_stats:
            serializer = TeamStatisticSerializers(team_stats)
            return Response(serializer.data)

        # If not found, fetch from API and update the database
        url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={team_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['response']
            league_id = data['league']['id']
            league_name = data['league']['name']
            league_country = data['league']['country']
            league_logo = data['league']['logo']
            league_flag = data['league']['flag']
            season = data['league']['season']
            form = data['form']
            fixtures = data['fixtures']
            goals = data['goals']
            biggest = data['biggest']
            clean_sheet = data['clean_sheet']
            failed_to_score = data['failed_to_score']
            penalty = data['penalty']
            lineups = data['lineups']
            cards = data['cards']

            # Create the Teams object if it doesn't exist
            team, created = Teams.objects.get_or_create(team_id=team_id)
            if created:
                team.team_name = data['team']['name']
                team.team_logo = data['team']['logo']
                team.save()

            # Create or update the TeamStatistics object
            team_stats, created = TeamStatistics.objects.get_or_create(
                team=team,  # Use the team object instead of team_id
                season=season,
                defaults={
                    'league_id': league_id,
                    'league_name': league_name,
                    'league_country': league_country,
                    'league_logo': league_logo,
                    'league_flag': league_flag,
                    'form': form,
                    'fixtures': fixtures,
                    'goals': goals,
                    'biggest': biggest,
                    'clean_sheet': clean_sheet,
                    'failed_to_score': failed_to_score,
                    'penalty': penalty,
                    'lineups': lineups,
                    'cards': cards,
                }
            )

            serializer = TeamStatisticSerializers(team_stats)
            return Response(serializer.data)

        else:
            return Response({"error": "Failed to fetch event data"}, status=response.status_code)


class PlayersView(APIView):
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

        # Check if team_id is provided
        if team_id:
            team_info = Teams.objects.filter(team_id=team_id).first()
            if not team_info:
                return Response({"error": "Team not found"}, status=404)
        else:
            # Fetch team information based on league and season
            team_info = Teams.objects.filter(season=season, league_id=league_id).first()
            if not team_info:
                return Response({"error": "Team not found"}, status=404)

        # Check if PlayersInformation objects already exist for this team and season
        player_infos = PlayersInformation.objects.filter(team_id=team_info, season=season)
        if player_infos.exists():
            serialized_data = PlayersInformationSerializers(player_infos, many=True).data
            return Response(serialized_data)

        # If not, construct the API request URL
        url = f"https://v3.football.api-sports.io/players?league={league_id}&season={season}&team={team_info.team_id}"

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

                    # Create a new PlayersInformation object
                    player_info = PlayersInformation.objects.create(
                        team_id=team_info.team_id,  # Assign the team_id field the id of the team_info object
                        season=season,
                        player=player,
                        statistics=player_stats
                    )
  # Return all PlayersInformation objects for this team and season
            player_infos = PlayersInformation.objects.filter(team_id=team_info, season=season)
            serialized_data = PlayersInformationSerializers(player_infos, many=True).data
            return Response(serialized_data)

        else:
            return Response({"error": "Failed to fetch player data"}, status=response.status_code)