import requests
headers = {'x-apisports-key': '85639a389857bcb9977a7ba7f5bed5ce'}
def get_year():
    yurl = 'https://v3.football.api-sports.io/leagues'
    params = {'id': 140, 'current': 'true'}
    headers= headers
    response = requests.get(yurl, headers=headers, params=params)
    res =response.json()
    res= res['response'][0]['seasons'][0]
    year = res['year']   
    return year

