from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Leagues, Season, LeagueTeams, Coach, Player, Fixture, FixtureStat, FixtureEvent, FixtureLineup, FixturePlayer
from .serializers import LeagueSerializer, TeamSerializer, CoachSerializer, PlayerSerializer, FixtureSerializer, FixtureStatSerializer, FixtureEventSerializer, FixtureLineupSerializer, FixturePlayerSerializer
import time
from .last import accheaders, myleague_ids, get_year
from googletrans import Translator
from django.db import transaction

class LeagueView(APIView):
    def get(self, request, league):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league"}, status=400)

        return self.get_league_data(league_id)

    def get_league_data(self, league_id):
        try:
            league_data = Leagues.objects.get(league_id=league_id)
            serializer = LeagueSerializer(league_data)
            return Response(serializer.data)
        except Leagues.DoesNotExist:
            return self.fetch_league_data_from_api(league_id)

    def fetch_league_data_from_api(self, league_id):
        url = f'https://v3.football.api-sports.io/leagues?id={league_id}'
        headers = accheaders
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()['response'][0]
            league_name = data['league']['name']
            league_enName = league_name.lower()

            # Using googletrans for translation
            translator = Translator()
            league_faName = translator.translate(league_name, dest='fa').text

            with transaction.atomic():
                league_data = Leagues.objects.create(
                    league_id=league_id,
                    league_name=league_name,
                    league_enName=league_enName,
                    league_faName=league_faName,
                    league_type=data['league']['type'],
                    league_logo=data['league']['logo'],
                    league_country=data['country'],
                    league_country_flag=data['country']['flag'],
                )
                if 'seasons' in data:
                    seasons = []
                    for season in data['seasons']:
                        seasons.append(Season(
                            league=league_data,
                            year=season['year'],
                            start=season['start'],
                            end=season['end'],
                        ))
                    Season.objects.bulk_create(seasons)
            serializer = LeagueSerializer(league_data)
            return Response(serializer.data)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch league data: " + str(e)}, status=500)
        except Exception as e:
            return Response({"error": "Failed to fetch league data: " + str(e)}, status=500)





class TeamView(APIView):
    def get(self, request, league, season=None):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league"}, status=400)
        if season is None:
            season = str(get_year())

        try:
            league_data = Leagues.objects.get(league_id=league_id)
            season_data = Season.objects.filter(league=league_data, year=season)
            if not season_data.exists():
                return Response({"error": "Invalid season1"}, status=400)

            teams = LeagueTeams.objects.filter(league_id=league_data, season__in=season_data)
            if teams.exists():
                serializer = TeamSerializer(teams, many=True)
                return Response(serializer.data)
            else:
                return self.get_teams_from_api(request, league_id, season)
        except Leagues.DoesNotExist:
            return Response({"error": "League data not found"}, status=404)

    def get_teams_from_api(self, request, league_id, season):
        url = f'https://v3.football.api-sports.io/teams?league={league_id}&season={season}'
        headers = accheaders
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['response']
            teams = []
            translator = Translator()
            for team in data:
                team_faName = translator.translate(team['team']['name'], dest='fa').text
                team_country_faName = translator.translate(team['team']['country'], dest='fa').text
                venue_faName = translator.translate(team['venue']['name'], dest='fa').text
                city_fa = translator.translate(team['venue']['city'], dest='fa').text
                team_data, created = LeagueTeams.objects.get_or_create(
                    team_id=team['team']['id'],
                    defaults={
                        'team_name': team['team']['name'],
                        'team_faName': team_faName,
                        'team_logo': team['team']['logo'],
                        'team_code': team['team']['code'],
                        'team_country': team['team']['country'],
                        'team_faCountry': team_country_faName,
                        'team_founded': team['team']['founded'],
                        'team_national': team['team']['national'],
                        'venue': {
                            'id': team['venue']['id'],
                            'name': team['venue']['name'],
                            'venue_faName': venue_faName,
                            'address': team['venue']['address'],
                            'city': team['venue']['city'],
                            'city_fa': city_fa,
                            'capacity': team['venue']['capacity'],
                            'surface': team['venue']['surface'],
                            'image': team['venue']['image'],
                        },
                        'league_id': Leagues.objects.get(league_id=league_id)
                    }
                )
                teams.append(team_data)
            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch team data"}, status=response.status_code)



class CoachView(APIView):
    def get(self, request, team_id):
        try:
            team_data = LeagueTeams.objects.get(team_id=team_id)
            coaches = Coach.objects.filter(team=team_data)
            if coaches.exists():
                serializer = CoachSerializer(coaches, many=True)
                return Response(serializer.data)
            else:
                return self.get_coaches_from_api(team_id)
        except LeagueTeams.DoesNotExist:
            return Response({"error": "Team data not found"}, status=404)

    def get_coaches_from_api(self, team_id):
        url = f'https://v3.football.api-sports.io/coachs?team={team_id}'
        headers = accheaders
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['response']
            coaches = []
            translator = Translator()
            for coach in data:
                coach_faName = translator.translate(coach['name'], dest='fa').text
                birth_faPlace = translator.translate(coach['birth']['place'], dest='fa').text
                birth_faCountry = translator.translate(coach['birth']['country'], dest='fa').text
                nationality_fa = translator.translate(coach['nationality'], dest='fa').text
                try:
                    team = LeagueTeams.objects.get(team_id=team_id)
                except LeagueTeams.DoesNotExist:
                    return Response({"error": "Team data not found"}, status=404)
                career = []
                for career_data in coach['career']:
                    career.append({
                        "team": career_data['team']['name'],
                        "start": career_data['start'],
                        "end": career_data['end']
                    })
                coach_data, created = Coach.objects.get_or_create(
                    coach_id=coach['id'],
                    defaults={
                        'name': coach['name'],
                        'faName': coach_faName,
                        'age': coach['age'],
                        'birth_date': coach['birth']['date'],
                        'birth_place': coach['birth']['place'],
                        'birth_faPlace': birth_faPlace,
                        'birth_country': coach['birth']['country'],
                        'birth_faCountry': birth_faCountry,
                        'nationality': coach['nationality'],
                        'faNationality': nationality_fa,
                        'photo': coach['photo'],
                        'team': team,
                        'career': career
                    }
                )
                coaches.append(coach_data)
            serializer = CoachSerializer(coaches, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch coach data"}, status=response.status_code)



class PlayerView(APIView):
    def get(self, request, league, team_id, season=None):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league"}, status=400)

        if season is None:
            season = str(get_year())

        try:
            league_data = Leagues.objects.get(league_id=league_id)
            season_data = Season.objects.get(league=league_data, year=season)
            team_data = LeagueTeams.objects.get(team_id=team_id, league_id=league_data)
        except (Leagues.DoesNotExist, Season.DoesNotExist, LeagueTeams.DoesNotExist):
            return Response({"error": "Invalid league, season or team"}, status=400)

        try:
            players = Player.objects.filter(team=team_data, season=season_data)
            if players.exists():
                serializer = PlayerSerializer(players, many=True)
                return Response(serializer.data)
            else:
                return self.get_players_from_api(request, league_id, team_id, season, team_data, season_data)
        except Player.DoesNotExist:
            return self.get_players_from_api(request, league_id, team_id, season, team_data, season_data)

    def get_players_from_api(self, request, league_id, team_id, season, team_data, season_data):
        url = f"https://v3.football.api-sports.io/players?league={league_id}&season={season}&team={team_id}"
        headers = accheaders

        # Create a Session object
        session = requests.Session()
        session.headers.update(headers)

        response = session.get(url)
        print(response.status_code)
        print(response.json())

        if response.status_code == 200:
            data = response.json()
            players = []
            translator = Translator()

            # Get the total number of pages
            total_pages = data['paging']['total']

            # Fetch all pages of players
            for page in range(1, total_pages + 1):
                page_url = f"{url}&page={page}"
                page_response = session.get(page_url)
                page_data = page_response.json()

                # Loop through each player in the response
                for player_data in page_data['response']:
                    player = player_data['player']
                    statistics = player_data['statistics'][0]

                    # Create a dictionary to store the player data
                    name_parts = player['name'].split()
                    firstname_parts = player['firstname'].split()

                    if len(firstname_parts) == 1:
                        name = f"{firstname_parts[0]} {name_parts[-1]}"
                    else:
                        for part in firstname_parts:
                            if part[0].lower() == name_parts[0][0].lower():
                                name = f"{part} {name_parts[-1]}"
                                break
                        else:
                            name = f"{firstname_parts[0]} {name_parts[-1]}"

                    player_dict = {
                        'player_id': player['id'],
                        'name': name,
                        'faName': translator.translate(name, dest='fa').text,
                        'age': player['age'],
                        'birthDate': player['birth']['date'],
                        'birthPlace': player['birth']['place'],
                        'faBirthPlace': translator.translate(player['birth']['place'], dest='fa').text,
                        'birthCountry': player['birth']['country'],
                        'faBirthCountry': translator.translate(player['birth']['country'], dest='fa').text,
                        'nationality': player['nationality'],
                        'faNationality': translator.translate(player['nationality'], dest='fa').text,
                        'height': player['height'],
                        'weight': player['weight'],
                        'injured': player['injured'],
                        'photo': player['photo'],
                        'team': team_data,
                        'season': season_data,
                        'appearences': statistics['games']['appearences'],
                        'lineups': statistics['games']['lineups'],
                        'minutes': statistics['games']['minutes'],
                        'number': statistics['games']['number'],
                        'position': statistics['games']['position'],
                        'rating': statistics['games']['rating'],
                        'captain': statistics['games']['captain'],
                        'substitutesIn': statistics['substitutes']['in'],
                        'substitutesOut': statistics['substitutes']['out'],
                        'bench': statistics['substitutes']['bench'],
                        'shotsTotal': statistics['shots']['total'],
                        'shotsOn': statistics['shots']['on'],
                        'goalsTotal': statistics['goals']['total'],
                        'goalsConceded': statistics['goals']['conceded'],
                        'assists': statistics['goals']['assists'],
                        'saves': statistics['goals']['saves'],
                        'passTotal': statistics['passes']['total'],
                        'passKey': statistics['passes']['key'],
                        'passAccuracy': statistics['passes']['accuracy'],
                        'tacklesTotal': statistics['tackles']['total'],
                        'blocks': statistics['tackles']['blocks'],
                        'interceptions': statistics['tackles']['interceptions'],
                        'duelsTotal': statistics['duels']['total'],
                        'duelsWon': statistics['duels']['won'],
                        'dribbleAttempts': statistics['dribbles']['attempts'],
                        'dribbleSuccess': statistics['dribbles']['success'],
                        'dribblePast': statistics['dribbles']['past'],
                        'foulsDrawn': statistics['fouls']['drawn'],
                        'foulsCommitted': statistics['fouls']['committed'],
                        'cardsYellow': statistics['cards']['yellow'],
                        'cardsYellowRed': statistics['cards']['yellowred'],
                        'cardsRed': statistics['cards']['red'],
                        'penaltyWon': statistics['penalty']['won'],
                        'penaltyCommited': statistics['penalty']['commited'],
                        'penaltyScored': statistics['penalty']['scored'],
                        'penaltyMissed': statistics['penalty']['missed'],
                        'penaltySaved': statistics['penalty']['saved'],
                    }

                    # Create or update the player in the database
                    player_obj, created = Player.objects.get_or_create(player_id=player['id'], defaults=player_dict)
                    if not created:
                        # If the player already exists, update its data
                        for key, value in player_dict.items():
                            setattr(player_obj, key, value)
                        player_obj.save()

                    players.append(player_obj)

            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch player data"}, status=response.status_code)
        



class FixtureView(APIView):
    def get(self, request, league, season=None):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league"}, status=400)
        if season is None:
            season = get_year()

        try:
            league_obj = Leagues.objects.get(league_id=league_id)
            season_obj = Season.objects.get(league=league_obj, year=season)
            fixtures = Fixture.objects.filter(league=league_obj, season=season_obj)
            if fixtures.exists():
                serializer = FixtureSerializer(fixtures, many=True)
                return Response(serializer.data)
            else:
                return self.get_update_fixture(league_id, season, league_obj, season_obj)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def get_update_fixture(self, league_id, season, league_obj, season_obj):
        url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            fixtures_data = data['response']

            # Create a list to store all fixture data
            fixtures_list = []

            translator = Translator()

            # Process each fixture and store in fixtures_list
            for fixture in fixtures_data:
                # Process fixture data here
                fixture_data = {
                    'fixture_id': fixture['fixture']['id'],
                    'fixture_referee': fixture['fixture']['referee'],
                    'fixture_timestamp': fixture['fixture']['timestamp'],
                    'fixture_periods_first': fixture['fixture']['periods']['first'],
                    'fixture_periods_second': fixture['fixture']['periods']['second'],
                    'fixture_venue_name': fixture['fixture']['venue']['name'],
                    'fixture_venue_faName': translator.translate(fixture['fixture']['venue']['name'], dest='fa').text,
                    'fixture_venue_city': fixture['fixture']['venue']['city'],
                    'fixture_venue_faCity': translator.translate(fixture['fixture']['venue']['city'], dest='fa').text,
                    'fixture_status_long': fixture['fixture']['status']['long'],
                    'fixture_status_short': fixture['fixture']['status']['short'],
                    'fixture_status_elapsed': fixture['fixture']['status']['elapsed'],
                    'league_round': fixture['league']['round'].split(' - ')[-1],
                    'teams_home': fixture['teams']['home']['id'],
                    'teams_home_winner': fixture['teams']['home']['winner'],
                    'teams_away': fixture['teams']['away']['id'],
                    'teams_away_winner': fixture['teams']['away']['winner'],
                    'goals': fixture['goals'],
                    'score_halftime': fixture['score']['halftime'],
                    'score_fulltime': fixture['score']['fulltime'],
                    'score_extratime': fixture['score']['extratime'],
                    'score_penalty': fixture['score']['penalty']
                }
                fixtures_list.append(fixture_data)

            # Calculate the maximum league round
            max_league_round = max(int(fixture['league_round']) for fixture in fixtures_list)

            # Update each fixture with the maximum league round
            for fixture in fixtures_list:
                fixture['league_round'] = f"{fixture['league_round']}/{max_league_round}"

            # Save fixtures to database
            for fixture in fixtures_list:
                fixture_obj, created = Fixture.objects.update_or_create(
                    fixture_id=fixture['fixture_id'],
                    defaults={
                        'league': league_obj,
                        'season': season_obj,
                        'fixture_referee': fixture['fixture_referee'],
                        'fixture_timestamp': fixture['fixture_timestamp'],
                        'fixture_periods_first': fixture['fixture_periods_first'],
                        'fixture_periods_second': fixture['fixture_periods_second'],
                        'fixture_venue_name': fixture['fixture_venue_name'],
                        'fixture_venue_faName': fixture['fixture_venue_faName'],
                        'fixture_venue_city': fixture['fixture_venue_city'],
                        'fixture_venue_faCity': fixture['fixture_venue_faCity'],
                        'fixture_status_long': fixture['fixture_status_long'],
                        'fixture_status_short': fixture['fixture_status_short'],
                        'fixture_status_elapsed': fixture['fixture_status_elapsed'],
                        'league_round': fixture['league_round'],
                        'teams_home_id': fixture['teams_home'],
                        'teams_home_winner': fixture['teams_home_winner'],
                        'teams_away_id': fixture['teams_away'],
                        'teams_away_winner': fixture['teams_away_winner'],
                        'goals': fixture['goals'],
                        'score_halftime': fixture['score_halftime'],
                        'score_fulltime': fixture['score_fulltime'],
                        'score_extratime': fixture['score_extratime'],
                        'score_penalty': fixture['score_penalty']
                    }
                )

                if created:
                    fixture_obj.save()

            serializer = FixtureSerializer(Fixture.objects.filter(league=league_obj, season=season_obj), many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
                    




class FixtureRoundView(APIView):
    def get(self, request, league, season=None, league_round=None):
        desired_league_ids = myleague_ids
        league_id = desired_league_ids.get(league)
        if league_id is None:
            return Response({"error": "Invalid league"}, status=400)

        # Call get_year() if season is None
        if season is None:
            season = get_year()

        try:
            # Get the league object
            league_obj = Leagues.objects.get(league_id=league_id)
            print(league_obj)

            # Get the season object
            season_obj = Season.objects.get(league=league_obj, year=int(season))
            print(season_obj)

            # Get fixtures for the specified league and season
            fixtures = Fixture.objects.filter(league=league_obj, season=season_obj)

            # Filter fixtures based on the league round 
            # (Assuming league_round is an integer)
            if league_round is not None:
                filtered_fixtures = fixtures.filter(
                    league_round__startswith=f"{league_round}/"
                )
            else:
                filtered_fixtures = fixtures

            if filtered_fixtures.exists():
                serializer = FixtureSerializer(filtered_fixtures, many=True)
                return Response(serializer.data)
            else:
                return Response({"message": "No fixtures found for the specified league, season, and round"}, status=404)
        except Season.DoesNotExist:
            return Response({"error": "Season not found"}, status=404)
        except Leagues.DoesNotExist:
            return Response({"error": "League not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class FixtureStatView(APIView):
    def get(self, request, fixture_id):
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        try:
            fixture_stat_data = FixtureStat.objects.filter(fixture=fixture_data)
            if fixture_stat_data.exists():
                serializer = FixtureStatSerializer(fixture_stat_data, many=True)
                return Response(serializer.data)
            else:
                return self.get_fixture_stat_from_api(request, fixture_id, fixture_data)
        except FixtureStat.DoesNotExist:
            return self.get_fixture_stat_from_api(request, fixture_id, fixture_data)

    def get_fixture_stat_from_api(self, request, fixture_id, fixture_data):
        url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            fixture_stat_list = []
            for team_data in data['response']:
                print("Team data:", team_data)
                if 'team' in team_data and 'id' in team_data['team'] and 'statistics' in team_data:
                    team_id = team_data['team']['id']
                    team_obj = LeagueTeams.objects.get(team_id=team_id)
                    fixture_stat_dict = {
                        'fixture': fixture_data,
                        'team': team_obj,
                        'ShotsOnGoal': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Shots on Goal'), None),
                        'ShotsOffGoal': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Shots off Goal'), None),
                        'ShotsInsideBox': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Shots insidebox'), None),
                        'ShotsOutsideBox': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Shots outsidebox'), None),
                        'TotalShots': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Total Shots'), None),
                        'BlockedShots': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Blocked Shots'), None),
                        'Fouls': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Fouls'), None),
                        'CornerKicks': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Corner Kicks'), None),
                        'Offsides': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Offsides'), None),
                        'BallPossession': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Ball Possession'), None),
                        'YellowCards': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Yellow Cards'), None),
                        'RedCards': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Red Cards'), None),
                        'GoalkeeperSaves': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Goalkeeper Saves'), None),
                        'Totalpasses': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Total passes'), None),
                        'Passesaccurate': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Passes accurate'), None),
                        'PassesPercent': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'Passes %'), None),
                        'ExpectedGoals': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'expected_goals'), None),
                        'GoalsPrevented': next((stat['value'] for stat in team_data['statistics'] if stat['type'] == 'goals_prevented'), None),
                    }
                    fixture_stat_list.append(fixture_stat_dict)
                else:
                    print("Invalid team data:", team_data)

            print("Fixture stat list:", fixture_stat_list)
            if fixture_stat_list:
                FixtureStat.objects.bulk_create([FixtureStat(**fixture_stat) for fixture_stat in fixture_stat_list])

                serializer = FixtureStatSerializer(FixtureStat.objects.filter(fixture=fixture_data), many=True)
                return Response(serializer.data)
            else :
                return Response({"error": "No fixture stats found"}, status=404)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
        except LeagueTeams.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        



class FixtureEventView(APIView):
    def get(self, request, fixture_id):
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        try:
            fixture_event_data = FixtureEvent.objects.filter(fixture=fixture_data)
            if fixture_event_data.exists():
                serializer = FixtureEventSerializer(fixture_event_data, many=True)
                return Response(serializer.data)
            else:
                return self.get_fixture_event_from_api(request, fixture_id, fixture_data)
        except FixtureEvent.DoesNotExist:
            return self.get_fixture_event_from_api(request, fixture_id, fixture_data)

    def get_fixture_event_from_api(self, request, fixture_id, fixture_data):
        url = f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            fixture_event_list = []
            for event_data in data['response']:
                team_obj = LeagueTeams.objects.get(team_id=event_data['team']['id'])
                if 'player' in event_data and event_data['player'] and 'id' in event_data['player']:
                    try:
                        player_obj = Player.objects.get(player_id=event_data['player']['id'])
                    except Player.DoesNotExist:
                        player_obj = None
                else:
                    player_obj = None
                if 'assist' in event_data and event_data['assist'] and 'id' in event_data['assist']:
                    try:
                        assist_obj = Player.objects.get(player_id=event_data['assist']['id'])
                    except Player.DoesNotExist:
                        assist_obj = None
                else:
                    assist_obj = None
                fixture_event_dict = {
                    'fixture': fixture_data,
                    'team': team_obj,
                    'player': player_obj,
                    'assist': assist_obj,
                    'type': event_data['type'],
                    'detail': event_data['detail'],
                    'comments': event_data['comments'],
                    'time_elapsed': event_data['time']['elapsed'],
                    'time_extra': event_data['time']['extra'],
                }
                fixture_event_list.append(fixture_event_dict)

            FixtureEvent.objects.bulk_create([FixtureEvent(**fixture_event) for fixture_event in fixture_event_list])

            serializer = FixtureEventSerializer(FixtureEvent.objects.filter(fixture=fixture_data), many=True)
            return Response(serializer.data)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
        except LeagueTeams.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)



class FixtureLineupView(APIView):
    def get(self, request, fixture_id):
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        try:
            fixture_lineup_data = FixtureLineup.objects.filter(fixture=fixture_data)
            if fixture_lineup_data.exists():
                serializer = FixtureLineupSerializer(fixture_lineup_data, many=True)
                return Response(serializer.data)
            else:
                return self.get_fixture_lineup_from_api(request, fixture_id, fixture_data)
        except FixtureLineup.DoesNotExist:
            return self.get_fixture_lineup_from_api(request, fixture_id, fixture_data)

    def get_fixture_lineup_from_api(self, request, fixture_id, fixture_data):
        url=f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            translator = Translator()
            fixture_lineup_list = []
            for team_data in data['response']:
                team_obj = LeagueTeams.objects.get(team_id=team_data['team']['id'])
                coach_name = team_data['coach']['name']
                coach_faName = translator.translate(coach_name, dest='fa').text
                coach_obj, created = Coach.objects.get_or_create(coach_id=team_data['coach']['id'], 
                                                                defaults={'name': coach_name, 'faName': coach_faName, 'photo': team_data['coach']['photo'], 'team': team_obj})
                team_color = team_data['team']['colors']
                fixture_lineup_dict = {
                    'fixture': fixture_data,
                    'team': team_obj,
                    'team_color': team_color,
                    'coach': coach_obj,
                    'formation': team_data['formation'],
                }
                fixture_lineup_list.append(fixture_lineup_dict )

            FixtureLineup.objects.bulk_create([FixtureLineup(**fixture_lineup) for fixture_lineup in fixture_lineup_list])

            for fixture_lineup in FixtureLineup.objects.filter(fixture=fixture_data):
                for team_data in data['response']:
                    if team_data['team']['id'] == fixture_lineup.team.team_id:
                        for player_data in team_data['startXI']:
                            player_obj = Player.objects.get(player_id=player_data['player']['id'])
                            player_obj.number = player_data['player']['number']
                            player_obj.position = player_data['player']['pos']
                            player_obj.grid = player_data['player']['grid']
                            player_obj.save()
                            fixture_lineup.start_xi.add(player_obj)

                        for player_data in team_data['substitutes']:
                            player_obj = Player.objects.get(player_id=player_data['player']['id'])
                            player_obj.number = player_data['player']['number']
                            player_obj.position = player_data['player']['pos']
                            player_obj.grid = player_data['player']['grid']
                            player_obj.save()
                            fixture_lineup.substitutes.add(player_obj)

            serializer = FixtureLineupSerializer(FixtureLineup.objects.filter(fixture=fixture_data), many=True)
            return Response(serializer.data)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
        except LeagueTeams.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=404)
        

class FixturePlayerView(APIView):
    def get(self, request, fixture_id):
        try:
            fixture_data = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        try:
            fixture_player_data = FixturePlayer.objects.filter(fixture=fixture_data)
            if fixture_player_data.exists():
                serializer = FixturePlayerSerializer(fixture_player_data, many=True)
                return Response(serializer.data)
            else:
                return self.get_fixture_player_from_api(request, fixture_id, fixture_data)
        except FixturePlayer.DoesNotExist:
            return self.get_fixture_player_from_api(request, fixture_id, fixture_data)

    def get_fixture_player_from_api(self, request, fixture_id, fixture_data):
        url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            fixture_player_list = []
            for team_data in data['response']:
                team_obj = LeagueTeams.objects.get(team_id=team_data['team']['id'])
                for player_data in team_data['players']:
                    player_obj = Player.objects.get(player_id=player_data['player']['id'])
                    statistics = player_data['statistics'][0]
                    fixture_player_dict = {
                        'fixture': fixture_data,
                        'team': team_obj,
                        'player': player_obj,
                        'minutes': statistics['games']['minutes'],
                        'rating': statistics['games']['rating'],
                        'captain': statistics['games']['captain'],
                        'substitute': statistics['games']['substitute'],
                        'shots_total': statistics['shots']['total'],
                        'shots_on': statistics['shots']['on'],
                        'goals_total': statistics['goals']['total'],
                        'goals_conceded': statistics['goals']['conceded'],
                        'assists': statistics['goals']['assists'],
                        'saves': statistics['goals']['saves'],
                        'passes_total': statistics['passes']['total'],
                        'passes_key': statistics['passes']['key'],
                        'passes_accuracy': statistics['passes']['accuracy'],
                        'tackles_total': statistics['tackles']['total'],
                        'blocks': statistics['tackles']['blocks'],
                        'interceptions': statistics['tackles']['interceptions'],
                        'duels_total': statistics['duels']['total'],
                        'duels_won': statistics['duels']['won'],
                        'dribbles_attempts': statistics['dribbles']['attempts'],
                        'dribbles_success': statistics['dribbles']['success'],
                        'dribbles_past': statistics['dribbles']['past'],
                        'fouls_drawn': statistics['fouls']['drawn'],
                        'fouls_committed': statistics['fouls']['committed'],
                        'cards_yellow': statistics['cards']['yellow'],
                        'cards_yellow_red': statistics['cards'].get('yellowred', 0),
                        'cards_red': statistics['cards']['red'],
                        'penalty_won': statistics['penalty']['won'],
                        'penalty_commited': statistics['penalty']['commited'],
                        'penalty_scored': statistics['penalty']['scored'],
                        'penalty_missed': statistics['penalty']['missed'],
                        'penalty_saved': statistics['penalty']['saved'],
                    }
                    fixture_player_list.append(fixture_player_dict)

                    # Update player number and position if they exist in the API data
                    if 'number' in statistics['games']:
                        player_obj.number = statistics['games']['number']
                    if 'position' in statistics['games']:
                        player_obj.position = statistics['games']['position']
                    player_obj.save()

            FixturePlayer.objects.bulk_create([FixturePlayer(**fixture_player) for fixture_player in fixture_player_list])

            serializer = FixturePlayerSerializer(FixturePlayer.objects.filter(fixture=fixture_data), many=True)
            return Response(serializer.data)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
        except LeagueTeams.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=404)
        




# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .models import Match, MatchStats, MatchesEvents, MatchesLineUps, MatchesPlayerStats
# from .serializers import MatchSerializer, MatchStatsSerializer, MatchEventsSerializer, MatchesLineUpSerializers, MatchPlayerStatSerializers
# import requests
# import re
# import json
# from fixtures.lastseason import get_today_date


# class MatchesAPIView(APIView):
#     def get(self, request, date=None):
#         desired_league_ids = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11,
#                               12, 13, 15, 16, 17, 18, 19, 20,
#                               21, 22, 23, 24, 25, 26, 27, 28,
#                               29, 30, 31, 32, 33, 34, 35, 36,
#                               37, 39, 45, 46, 48, 61, 65, 66,
#                               71, 73, 78, 81, 88, 90, 94, 96,
#                               98, 101, 102, 128, 130, 135, 137,
#                               140, 143, 203, 206, 253, 257, 290,
#                               291, 292, 294, 301, 302, 305, 307,
#                               480, 482, 483, 495, 504, 528, 529,
#                               531, 532, 533, 541, 543, 547, 548,
#                               550, 551, 556, 803, 804, 808, 810,
#                               826, 896, 905, 1089, 1105,
#                             ]

#         # If date is not provided, use today's date
#         if date is None:
#             date_str = get_today_date()
#         else:
#             # Use regex to extract the date from the URL
#             pattern = r'\d{4}-\d{2}-\d{2}'
#             match = re.search(pattern, date)
#             if match:
#                 date_str = match.group(0)
#             else:
#                 return Response({'error': 'Invalid date format.'}, status=400)

#         # Make a request to the API with the date as a parameter
#         url = 'https://v3.football.api-sports.io/fixtures'
#         headers = {
#             'x-rapidapi-host': 'v3.football.api-sports.io',
#             'x-rapidapi-key': '027bd46abc28e9a53c6789553b53f2d2'
#         }
#         params = {'date': date_str}
#         response = requests.get(url, headers=headers, params=params)
#         data = response.json()
#         # Process the data and filter by league id
#         matches = data['response']
#         filtered_matches = [] 
#         for match in matches: 
#             if match['league']['id'] in desired_league_ids: 
#                 # Get or create a Match instance with the desired match data 
#                 selected_match_data = { 
#                     'fixture_id' : match['fixture']['id'],
#                     'match_date' : match['fixture']['date'],
#                     'match_timestamp': match['fixture']['timestamp'],
#                     'match_periods_first': match['fixture']['periods']['first'],
#                     'match_periods_second' : match['fixture']['periods']['second'],
#                     'match_venue_name' : match['fixture']['venue']['name'],
#                     'match_venue_city' : match['fixture']['venue']['city'],
#                     'match_status_long' : match['fixture']['status']['long'],
#                     'league_id': match['league']['id'],
#                     'league_name' : match['league']['name'],
#                     'league_country' : match['league']['country'],
#                     'league_logo' : match['league']['logo'],
#                     'league_flag' : match['league']['flag'],
#                     'league_season' : match['league']['season'],
#                     'league_round' : match['league']['round'],
#                     'home_team_name' : match['teams']['home']['name'],
#                     'home_team_logo' : match['teams']['home']['logo'],
#                     'home_team_winner': match['teams']['home']['winner'],
#                     'away_team_name' : match['teams']['away']['name'],
#                     'away_team_logo' : match['teams']['away']['logo'],
#                     'away_team_winner': match['teams']['away']['winner'],
#                     'home_team_goals' : match['goals']['home'],
#                     'away_team_goals' : match['goals']['away'],
#                     'halftime_score' : match['score']['halftime'],
#                     'fulltime_score' : match['score']['fulltime'],
#                     'match_refree' : match['fixture']['referee']   # Add other fields accordingly 
#                 } 
#                 match_instance, created = Match.objects.get_or_create(
#                     match_date=selected_match_data['match_date'],
#                     home_team_name=selected_match_data['home_team_name'],
#                     away_team_name=selected_match_data['away_team_name'],
#                     defaults=selected_match_data
#                 )

#                 if not created:
#                     # Update the existing match instance with the new data
#                     for key, value in selected_match_data.items():
#                         setattr(match_instance, key, value)
#                     match_instance.save()
#                 filtered_matches.append(selected_match_data) 
#         # Serialize the filtered matches and return a JSON response 
#         serializer = MatchSerializer(filtered_matches, many=True)
#         return Response(serializer.data)