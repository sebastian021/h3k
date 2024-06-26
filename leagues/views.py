from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Leagues
from teams.views import TeamsView
from .serializers import LeagueSerializers
from googletrans import Translator
import json


class LeaguesView(APIView):
    def get(self, request, league):
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

        try:
            league_data = Leagues.objects.get(league_id=league_id)
            serializer = LeagueSerializers(league_data)
            return Response(serializer.data)
        except Leagues.DoesNotExist:
            url = f'https://v3.football.api-sports.io/leagues?id={league_id}'
            headers = {
                'x-rapidapi-host': 'v3.football.api-sports.io',
                'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['response'][0]
                league_name = data['league']['name']
                league_enName = league_name.lower()
                translator = Translator()  # Create a Translator instance
                league_faName = translator.translate(league_name, dest='fa').text  # Translate to Persian

                seasons_dict = {
                    str(season['year']): {  # Using the year as the key
                        'start': season['start'],
                        'end': season['end'],
                    }
                    for season in data['seasons']
                    }

                teams_view = TeamsView()
                teams_response = teams_view.get(request, league)
                num_teams = len(teams_response.data)

                num_rounds = (num_teams - 1) * 2 if data['league']['type'] == 'League' else None

                league_data = Leagues.objects.create(
                    league_id=league_id,
                    league_name=league_name,
                    league_enName=league_enName,
                    league_faName=league_faName,
                    league_type=data['league']['type'],
                    league_logo=data['league']['logo'],
                    league_country=data['country'],
                    seasons=json.dumps(seasons_dict),
                    num_teams=num_teams,
                    num_rounds=num_rounds,
                )
                serializer = LeagueSerializers(league_data)
                return Response(serializer.data)
            else:
                return Response({"error": "Failed to fetch league data"}, status=response.status_code)