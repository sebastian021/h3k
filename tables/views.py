import requests
from .models import Standing
from .serializers import StandingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from league.last import get_year
def fetch_and_save_standings(league_name, season=None):
    desired_league_ids = {
        'PremierLeague': 39,
        'Bundesliga': 78,
        'Laliga': 140,
        'SerieA': 135,
        'Ligue1': 61
    }
    
    league_id = desired_league_ids.get(league_name)
    
    if not league_id:
        return None
    
    if not season:
        # Default to current season
        season = get_year()
    
    url = f'https://v3.football.api-sports.io/standings?league={league_id}&season={season}'
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        data = data['response'][0]
        data = data['league']
        
        # Check if the data already exists in the database
        existing_standing = Standing.objects.filter(league_id=data['id'], league_season=data['season']).first()
        
        if existing_standing:
            existing_standing.league_name = data['name']
            existing_standing.league_country = data['country']
            existing_standing.league_logo = data['logo']
            existing_standing.league_flag = data['flag']
            existing_standing.standings_data = data['standings'][0]
            existing_standing.save()  # Update the existing record
            return existing_standing
        else:
            standing = Standing.objects.create(
                league_id=data['id'],
                league_name=data['name'],
                league_country=data['country'],
                league_logo=data['logo'],
                league_flag=data['flag'],
                league_season=data['season'],
                standings_data=data['standings'][0]
            )
            return standing
    else:
        return None

class StandingView(APIView):
    def get(self, request, league_name, season=None):
        standing = fetch_and_save_standings(league_name, season)
        
        if not standing:
            return Response({'message': 'Error fetching standings data'}, status=500)
        
        serializer = StandingSerializer(standing)
        
        return Response(serializer.data)
