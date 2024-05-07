import requests

headers = { 'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2' }

def get_year():
    yurl = 'https://v3.football.api-sports.io/leagues'
    params = {'id': 140, 'current': 'true'}
    
    response = requests.get(yurl, headers=headers, params=params)
    res = response.json()
    res = res['response'][0]['seasons'][0]
    year = res['year']
    
    return year