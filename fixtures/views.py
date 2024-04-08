from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Fixtures
import requests

class FixturesView(APIView):
    def get(self, request, league_name):
        desired_league_ids = {
            'PremierLeague': 39,
            'Bundesliga': 78,
            'Laliga': 140,
            'SerieA': 135,
            'Ligue1': 61
        }
        
        league_id = desired_league_ids.get(league_name)
        if not league_id:
            return Response({'error': 'Invalid league name'}, status=400)
        
        url = f'https://v3.football.api-sports.io/fixtures?league={league_id}&season=2023'
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        for fixture in data['response']:
            fixture_id = fixture['fixture']['id']
            
            obj, created = Fixtures.objects.get_or_create(
                fixture_id=fixture_id,
                defaults={
                    'league_id': league_id,
                    'league_name': league_name,
                    'league_season': 2023,
                    'league_round': fixture['league']['round'],
                    'fixture_timestamp': fixture['fixture']['timestamp']
                }
            )
            
            if not created:
                obj.league_round = fixture['league']['round']
                obj.fixture_timestamp = fixture['fixture']['timestamp']
                obj.save()
        
        return Response(data)
