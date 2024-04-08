import requests
from .models import Fixtures

def fetch_and_save_fixtures(league_name):
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

    url = f'https://v3.football.api-sports.io/fixtures?league={league_id}&season=2023'
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        fixture_data = response.json().get('response')
        
        for fixture in fixture_data:
            fixture_id = fixture_data['fixture']['id']
            existing_fixture, created = Fixtures.objects.get_or_create(fixture_id=fixture_id, defaults={
                'league_id': fixture_data['fixture']['league']['id'],
                'league_name': fixture_data['fixture']['league']['name'],
                'league_season': fixture_data['fixture']['league']['season'],
                'league_round': fixture_data['fixture']['league']['round'],
                'fixture_id': fixture_data['fixture']['id'],
                'fixture_timestamp': fixture_data['fixture']['timestamp']
            })
            if not created:
                existing_fixture.league_id = fixture_data['fixture']['league']['id']
                existing_fixture.league_name = fixture_data['fixture']['league']['name']
                existing_fixture.league_season = fixture_data['fixture']['league']['season']
                existing_fixture.league_round = fixture_data['fixture']['league']['round']
                existing_fixture.fixture_id = fixture_data['fixture']['id']
                existing_fixture.fixture_timestamp = fixture_data['fixture']['timestamp']
                existing_fixture.save()

        return list(Fixtures.objects.filter(fixture_id=fixture_id))
    else:
        return None
