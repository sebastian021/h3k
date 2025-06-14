import logging
from googletrans import Translator
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import *
from .serializers import *
from .last import accheaders, myleague_ids, get_year, get_today_date
from datetime import datetime
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)



class LeagueListView(APIView):
    def get(self, request):
        leagues_data = []

        for league_symbol, league_id in myleague_ids.items():
            try:
                # Try to get the league data from the database
                league_data = League.objects.get(league_id=league_id)
                leagues_data.append({
                    "id": league_data.league_id,
                    "symbol": league_symbol,
                    "enName": league_data.league_enName,
                    "faName": league_data.league_faName,
                    "logo": league_data.league_logo
                })
            except League.DoesNotExist:
                # If the league does not exist, fetch it from the LeagueView
                league_response = LeagueView().fetch_league_data_from_api(league_id)
                
                if league_response.status_code == 200:
                    # After fetching, try to get the league data again
                    league_data = League.objects.get(league_id=league_id)
                    leagues_data.append({
                        "id": league_data.league_id,
                        "symbol": league_symbol,
                        "enName": league_data.league_enName,
                        "faName": league_data.league_faName,
                        "logo": league_data.league_logo
                    })
                else:
                    # Handle the error response if fetching failed
                    return league_response

        return Response(leagues_data)

class LeagueView(APIView):
    def get(self, request, league_id):
        try:
            league = League.objects.get(league_id=league_id)
            serializer = LeagueSerializer(league)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except League.DoesNotExist:
            # Fetch from API and save if not exists
            response = self.fetch_league_data_from_api(league_id)
            if response.status_code == 200:
                # Try to get the league again after saving
                league = League.objects.get(league_id=league_id)
                serializer = LeagueSerializer(league)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response

    def fetch_league_data_from_api(self, league_id):
        url = f'https://v3.football.api-sports.io/leagues?id={league_id}'
        headers = accheaders
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()

            # Check if 'response' exists and is not empty
            if 'response' in data and len(data['response']) > 0:
                data = data['response'][0]
                symbol = data['league']['name']
                league_enName = symbol.lower()

                # Using googletrans for translation
                translator = Translator()
                league_faName = translator.translate(symbol, dest='fa').text
                country_name = data['country']['name']
                league_faCountry = translator.translate(country_name, dest='fa').text  # Translate country name to Persian

                with transaction.atomic():
                    league_data = League.objects.create(
                        league_id=league_id,
                        symbol=symbol,
                        league_enName=league_enName,
                        league_faName=league_faName,
                        league_type=data['league']['type'],
                        league_logo=data['league']['logo'],
                        league_country=data['country'],
                        league_faCountry=league_faCountry,
                        league_country_flag=data['country']['flag'],
                    )
                    if 'seasons' in data:
                        seasons = []
                        for season in data['seasons']:
                            seasons.append(Season(
                                league=league_data,
                                year=season['year'],
                            ))
                        Season.objects.bulk_create(seasons)

                return Response({
                    "league_id": league_data.league_id,
                    "symbol": league_data.symbol,
                    "league_enName": league_data.league_enName,
                    "league_faName": league_data.league_faName,
                    "league_type": league_data.league_type,
                    "league_logo": league_data.league_logo,
                    "faCountry": league_faCountry,
                    "league_country": {
                        "code": data['country']['code'],
                        "flag": data['country']['flag'],
                        "name": country_name,
                    },
                    "league_country_flag": league_data.league_country_flag,
                })
            else:
                return Response({"error": "No league data found for the given league ID."}, status=404)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch league data: " + str(e)}, status=500)
        except Exception as e:
            return Response({"error": "Failed to fetch league data: " + str(e)}, status=500)


class TeamView(APIView):
    def get(self, request, league_id, season=None):
        if season is None:
            season = str(get_year())

        # Check if the league exists in the database
        if not League.objects.filter(league_id=league_id).exists():
            # If league_id exists in myleague_ids, fetch from API and save it
            league_response = LeagueView().fetch_league_data_from_api(league_id)
            if league_response.status_code != 200:
                return league_response  # Return the error response from LeagueView

        try:
            league_data = League.objects.get(league_id=league_id)
            season_data = Season.objects.filter(league=league_data, year=season)

            if not season_data.exists():
                return Response({"error": "Invalid season"}, status=400)

            teams = TeamLeague.objects.filter(league=league_data, season__in=season_data).select_related('team')
            if teams.exists():
                serializer = TeamSerializer([team_league.team for team_league in teams], many=True)
                return Response(serializer.data)
            else:
                return self.get_teams_from_api(request, league_id, season)
        except League.DoesNotExist:
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
                team_faName = translator.translate("The " + team['team']['name'], src='en', dest='fa').text
                team_country_faName = translator.translate(team['team']['country'], src='en', dest='fa').text
                venue_faName = translator.translate(team['venue']['name'], src='en',  dest='fa').text
                city_fa = translator.translate(team['venue']['city'], dest='fa').text
                
                team_data, created = Team.objects.get_or_create(
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
                            'name': team['venue']['name'],
                            'venue_faName': venue_faName,
                            'address': team['venue']['address'],
                            'city': team['venue']['city'],
                            'city_fa': city_fa,
                            'capacity': team['venue']['capacity'],
                            'image': team['venue']['image'],
                        },
                    }
                )

                # Create or update the TeamLeague relationship
                season_instance = Season.objects.get(league_id=league_id, year=season)
                TeamLeague.objects.get_or_create(team=team_data, league_id=league_id, season=season_instance)

                teams.append(team_data)

            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch team data"}, status=response.status_code)


class TeamIDView(APIView):
    def get(self, request, team_id):
        # Check if the team exists in the database
        team_instance = Team.objects.filter(team_id=team_id).first()
        if team_instance:
            # If the team exists, serialize and return the data
            serializer = TeamSerializer(team_instance)
            return Response(serializer.data)

        # If the team does not exist, fetch it from the external API
        return self.fetch_team_from_api(team_id)

    def fetch_team_from_api(self, team_id):
        url = f'https://v3.football.api-sports.io/teams?id={team_id}'
        headers = accheaders  # Use the provided headers for API calls

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            # Check for valid response
            if 'response' not in data or not data['response']:
                return Response({"error": "No team data found for this team ID."}, status=status.HTTP_404_NOT_FOUND)

            team_data = data['response'][0]  # Extract the first team's data
            team_info = team_data['team']
            venue_info = team_data['venue']

            # Translate necessary fields
            translator = Translator()
            team_faName = translator.translate("The " + team_info['name'], src='en', dest='fa').text
            team_country_faName = translator.translate(team_info['country'], src='en', dest='fa').text
            venue_faName = translator.translate(venue_info['name'], src='en', dest='fa').text
            city_fa = translator.translate(venue_info['city'], src='en', dest='fa').text

            # Create or update the Team instance
            team_instance, created = Team.objects.update_or_create(
                team_id=team_info['id'],
                defaults={
                    'team_name': team_info['name'],
                    'team_faName': team_faName,
                    'team_logo': team_info['logo'],
                    'team_code': team_info['code'],
                    'team_country': team_info['country'],
                    'team_faCountry': team_country_faName,
                    'team_founded': team_info.get('founded', None),
                    'team_national': team_info.get('national', False),
                    'venue': {
                        'name': venue_info['name'],
                        'venue_faName': venue_faName,
                        'address': venue_info['address'],
                        'city': venue_info['city'],
                        'city_fa': city_fa,
                        'capacity': venue_info['capacity'],
                        'image': venue_info['image'],
                    },
                }
            )

            # Serialize and return the team data
            serializer = TeamSerializer(team_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch team data: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class TeamStatView(APIView):
    def get(self, request, league_id, team_id, season=None):
        # Check if season is provided, if not use get_year()
        if not season:
            season = get_year()

        # Check if league exists
        if not League.objects.filter(league_id=league_id).exists():
            league_response = LeagueView().fetch_league_data_from_api(league_id)
            if league_response.status_code != 200:
                return league_response  # Return error response if league fetch fails

        # Check if team exists
        if not Team.objects.filter(team_id=team_id).exists():
            team_response = TeamView().get_teams_from_api(request, league_id, season)
            if team_response.status_code != 200:
                return team_response  # Return error response if team fetch fails

        # Check if season exists
        season_instance = Season.objects.filter(year=season).first()
        if not season_instance:
            return Response({"error": "Season does not exist"}, status=400)

        # Check if TeamStat already exists
        team_stat = TeamStat.objects.filter(league_id=league_id, team_id=team_id, season=season_instance).first()
        if team_stat:
            serializer = TeamStatSerializer(team_stat)
            return Response(serializer.data)
        else:
            # Fetch statistics from the API
            return self.fetch_team_statistics(league_id, team_id, season_instance)


    def fetch_team_statistics(self, league_id, team_id, season):
        url = f'https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season.year}&team={team_id}'
        headers = accheaders
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if 'response' not in data:
                return Response({"error": "Invalid response structure from API"}, status=400)

            response_data = data['response']

            # Ensure the required keys exist in the response data
            if 'league' not in response_data or 'team' not in response_data or 'fixtures' not in response_data:
                return Response({"error": "Missing data in API response"}, status=400)

            league_data = response_data['league']
            team_data = response_data['team']
            stats = response_data['fixtures']
            
            # Check if 'goals' key exists in stats
            goals = response_data.get('goals', {})
            
            # Extract goals data safely
            goals_for_total = goals.get('for', {}).get('total', {})
            goals_against_total = goals.get('against', {}).get('total', {})

            # Create or update TeamStat
            team_stat, created = TeamStat.objects.update_or_create(
                league=League.objects.get(league_id=league_data['id']),
                team=Team.objects.get(team_id=team_data['id']),
                season=season,
                defaults={
                    'form': response_data.get('form', None),
                    'fixtures_played_home': stats['played'].get('home', 0),
                    'fixtures_played_away': stats['played'].get('away', 0),
                    'fixtures_played_total': stats['played'].get('total', 0),
                    'wins_home': stats['wins'].get('home', 0),
                    'wins_away': stats['wins'].get('away', 0),
                    'wins_total': stats['wins'].get('total', 0),
                    'draws_home': stats['draws'].get('home', 0),
                    'draws_away': stats['draws'].get('away', 0),
                    'draws_total': stats['draws'].get('total', 0),
                    'losses_home': stats['loses'].get('home', 0),
                    'losses_away': stats['loses'].get('away', 0),
                    'losses_total': stats['loses'].get('total', 0),
                    'goals_for_home': goals_for_total.get('home', 0),
                    'goals_for_away': goals_for_total.get('away', 0),
                    'goals_for_total': goals_for_total.get('total', 0),
                    'goals_against_home': goals_against_total.get('home', 0),
                    'goals_against_away': goals_against_total.get('away', 0),
                    'goals_against_total': goals_against_total.get('total', 0),
                    'clean_sheet_home': stats.get('clean_sheet', {}).get('home', 0),
                    'clean_sheet_away': stats.get('clean_sheet', {}).get('away', 0),
                    'clean_sheet_total': stats.get('clean_sheet', {}).get('total', 0),
                    'failed_to_score_home': stats.get('failed_to_score', {}).get('home', 0),
                    'failed_to_score_away': stats.get('failed_to_score', {}).get('away', 0),
                    'failed_to_score_total': stats.get('failed_to_score', {}).get('total', 0),
                    'penalties_scored_total': stats.get('penalty', {}).get('scored', {}).get('total', 0),
                    'penalties_missed_total': stats.get('penalty', {}).get('missed', {}).get('total', 0),
                }
            )

            # Return the data to the frontend
            serializer = TeamStatSerializer(team_stat)
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to fetch team statistics"}, status=response.status_code)



class CoachView(APIView):
    def get(self, request, team_id):
        try:
            team_data = Team.objects.get(team_id=team_id)
            coaches = Coach.objects.filter(team=team_data)
            if coaches.exists():
                serializer = CoachSerializer(coaches, many=True)
                return Response(serializer.data)
            else:
                return self.get_coaches_from_api(team_id)
        except Team.DoesNotExist:
            # Try to fetch and create the team, then retry
            TeamIDView().fetch_team_from_api(team_id)
            try:
                team_data = Team.objects.get(team_id=team_id)
                coaches = Coach.objects.filter(team=team_data)
                if coaches.exists():
                    serializer = CoachSerializer(coaches, many=True)
                    return Response(serializer.data)
                else:
                    return self.get_coaches_from_api(team_id)
            except Team.DoesNotExist:
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
                # Extract last name from the full name
                full_name = coach['name']
                last_name = "Mr."+full_name.split()[-1]  # Get the last part of the name
                
                # Translate last name to Persian
                last_name_fa = translator.translate(last_name,src='en', dest='fa').text
                lastNameFa = last_name_fa.split()[-1]
                
                # Translate other details
                birth_faPlace = translator.translate(coach['birth']['place'], dest='fa').text
                birth_faCountry = translator.translate(coach['birth']['country'], dest='fa').text
                nationality_fa = translator.translate(coach['nationality'], dest='fa').text
                
                try:
                    team = Team.objects.get(team_id=team_id)
                except Team.DoesNotExist:
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
                        'name': full_name,
                        'faName': lastNameFa,  # Use translated last name
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


    def get_coach_id_api(self, coach_id):
        url = f'https://v3.football.api-sports.io/coachs?id={coach_id}'
        headers = accheaders
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['response']
            if not data:
                return
            coach = data[0]
            translator = Translator()
            last_name = "Mr." + coach['name'].split()[-1]
            last_name_fa = translator.translate(last_name, src='en', dest='fa').text
            lastNameFa = last_name_fa.split()[-1]
            birth_faPlace = translator.translate(coach['birth']['place'], dest='fa').text
            birth_faCountry = translator.translate(coach['birth']['country'], dest='fa').text
            nationality_fa = translator.translate(coach['nationality'], dest='fa').text

            # Find current team from 'career' (where end is null)
            team_obj = None
            if 'career' in coach:
                for career_entry in coach['career']:
                    if career_entry.get('end') is None and 'team' in career_entry:
                        team_id = career_entry['team']['id']
                        team_obj = Team.objects.filter(team_id=team_id).first()
                        if not team_obj:
                            TeamIDView().fetch_team_from_api(team_id)
                            team_obj = Team.objects.filter(team_id=team_id).first()
                        break
            # Fallback: try 'team' field if no career found
            if not team_obj and 'team' in coach and coach['team']:
                team_id = coach['team']['id']
                team_obj = Team.objects.filter(team_id=team_id).first()
                if not team_obj:
                    TeamIDView().fetch_team_from_api(team_id)
                    team_obj = Team.objects.filter(team_id=team_id).first()

            Coach.objects.get_or_create(
                coach_id=coach['id'],
                defaults={
                    'name': coach['name'],
                    'faName': lastNameFa,
                    'age': coach['age'],
                    'birth_date': coach['birth']['date'],
                    'birth_place': coach['birth']['place'],
                    'birth_faPlace': birth_faPlace,
                    'birth_country': coach['birth']['country'],
                    'birth_faCountry': birth_faCountry,
                    'nationality': coach['nationality'],
                    'faNationality': nationality_fa,
                    'photo': coach['photo'],
                    'team': team_obj,  # Set to current team or None
                }
            )

class PlayerView(APIView):
    def get(self, request, team_id, season=None):
        if season is None:
            season = str(get_year())

        # First, get the season instance
        season_instance = Season.objects.filter(year=season).first()
        if not season_instance:
            return Response({"error": "Invalid season."}, status=404)

        # Now query PlayerTeam to find players associated with the team and season
        player_teams = PlayerTeam.objects.filter(team__team_id=team_id, season=season_instance)

        # Get the player instances from the filtered PlayerTeam queryset
        players = [player_team.player for player_team in player_teams]

        if players:
            serializer = AllPlayerSerializer(players, many=True)
            return Response(serializer.data)

        # If players do not exist, fetch from API
        return self.get_players_from_api(team_id, season_instance)

    def get_players_from_api(self, team_id, season):
        url = f'https://v3.football.api-sports.io/players?season={season.year}&team={team_id}'  # Use year from season
        headers = accheaders
        all_players = []
        current_page = 1

        while True:
            try:
                response = requests.get(url + f"&page={current_page}", headers=headers, timeout=10)
                response.raise_for_status()  # Raise an error for bad responses
                
                data = response.json()
                all_players.extend(data['response'])

                # Check if there are more pages
                if current_page >= data['paging']['total']:
                    break
                current_page += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching player data: {e}")
                return Response({"error": "Failed to fetch player data"}, status=500)

        # Process and save players
        players = self.save_players(all_players, team_id, season)

        # After saving, query the database to retrieve the saved players
        serializer = AllPlayerSerializer(players, many=True)
        return Response(serializer.data)
    def save_players(self, all_players, team_id, season):
        translator = Translator()
        players_data = []
        
        birth_places = []
        birth_countries = []
        nationalities = []
        names_to_translate = []

        # Gather data for translation
        for player_data in all_players:
            player = player_data['player']
            name_parts = player['name'].split()
            firstname_parts = player['firstname'].split()

            # Build the player name
            if len(firstname_parts) == 1:
                name = f"{firstname_parts[0]} {name_parts[-1]}"
            else:
                for part in firstname_parts:
                    if part[0].lower() == name_parts[0][0].lower():
                        name = f"{part} {name_parts[-1]}"
                        break
                else:
                    name = f"{firstname_parts[0]} {name_parts[-1]}"

            # Collect data for each player
            players_data.append({
                'player_id': player['id'],
                'name': name,
                'age': player['age'],
                'birthDate': player['birth']['date'],
                'birthPlace': player['birth']['place'],
                'birthCountry': player['birth']['country'],
                'nationality': player['nationality'],
                'height': player['height'],
                'weight': player['weight'],
                'injured': player['injured'],
                'photo': player['photo'],
            })

            # Collect fields for translation
            birth_places.append(player['birth']['place'])
            birth_countries.append(player['birth']['country'])
            nationalities.append(player['nationality'])
            names_to_translate.append(name)

        # Translate all at once
        fa_names = translator.translate(names_to_translate, dest='fa')
        fa_birth_places = translator.translate(birth_places, dest='fa')
        fa_birth_countries = translator.translate(birth_countries, dest='fa')
        fa_nationalities = translator.translate(nationalities, dest='fa')

        # Map translations back to players
        for i, player in enumerate(players_data):
            player['faName'] = fa_names[i].text
            player['faBirthPlace'] = fa_birth_places[i].text
            player['faBirthCountry'] = fa_birth_countries[i].text
            player['faNationality'] = fa_nationalities[i].text

        # Save players to the database and link to Team and Season
        saved_players = []
        with transaction.atomic():
            for player in players_data:
                # Create or update the player
                player_instance, created = Player.objects.update_or_create(
                    player_id=player['player_id'],
                    defaults={
                        'name': player['name'],
                        'faName': player['faName'],
                        'age': player['age'],
                        'birthDate': player['birthDate'],
                        'birthPlace': player['birthPlace'],
                        'faBirthPlace': player['faBirthPlace'],  # Save faBirthPlace
                        'birthCountry': player['birthCountry'],
                        'faBirthCountry': player['faBirthCountry'],  # Save faBirthCountry
                        'nationality': player['nationality'],
                        'faNationality': player['faNationality'],  # Save faNationality
                        'height': player['height'],
                        'weight': player['weight'],
                        'injured': player['injured'],
                        'photo': player['photo'],
                    }
                )
                saved_players.append(player_instance)

                # Create or update PlayerTeam entry
                PlayerTeam.objects.get_or_create(
                    player=player_instance,
                    team_id=team_id,
                    season=season
                )
        return saved_players





class PlayerProfileView(APIView):
    def get(self, request, player_id):
        try:
            player = Player.objects.get(player_id=player_id)
            serializer = PlayerProfileSerializer(player)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Player.DoesNotExist:
            return self.get_player_from_api(player_id)

    def get_player_from_api(self, player_id):
        # Construct the URL for fetching player profile from the external API
        url = f'https://v3.football.api-sports.io/players/profiles?player={player_id}'
        
        try:
            response = requests.get(url, headers=accheaders)  # Use the predefined headers
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch player data from API."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check for valid response
        if 'response' not in data or not data['response']:
            return Response({"error": "No player data found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract player data from the response
        player_data = data['response'][0]['player']

        # Create or update the player in the local database
        player = self.save_player_data(player_data)

        # Serialize and return the newly created player data
        serializer = PlayerProfileSerializer(player)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def save_player_data(self, player_data):
        # Build the player name according to the specified rules
        name_parts = player_data['name'].split()
        firstname_parts = player_data['firstname'].split()

        # Build the player name
        if len(firstname_parts) == 1:
            name = f"{firstname_parts[0]} {name_parts[-1]}"
        else:
            for part in firstname_parts:
                if part[0].lower() == name_parts[0][0].lower():
                    name = f"{part} {name_parts[-1]}"
                    break
            else:
                name = f"{firstname_parts[0]} {name_parts[-1]}"

        # Translate the name and other fields
        translator = Translator()
        fa_name = translator.translate(name, dest='fa').text
        fa_birth_place = translator.translate(player_data['birth']['place'], dest='fa').text
        fa_birth_country = translator.translate(player_data['birth']['country'], dest='fa').text
        fa_nationality = translator.translate(player_data['nationality'], dest='fa').text

        # Create or update the player instance
        player_instance, created = Player.objects.update_or_create(
            player_id=player_data['id'],
            defaults={
                'name': name,
                'faName': fa_name,
                'age': player_data.get('age'),
                'birthDate': player_data['birth'].get('date'),
                'birthPlace': player_data['birth'].get('place'),
                'faBirthPlace': fa_birth_place,
                'birthCountry': player_data['birth'].get('country'),
                'faBirthCountry': fa_birth_country,
                'nationality': player_data.get('nationality'),
                'faNationality': fa_nationality,
                'height': player_data.get('height'),
                'weight': player_data.get('weight'),
                'number': player_data.get('number'),
                'position': player_data.get('position'),
                'photo': player_data.get('photo'),
                'injured': player_data.get('injured', False)  # Default to False if not provided
            }
        )

        return player_instance




class SquadView(APIView):
    def get(self, request, team_id):
        squad_players = Squad.objects.filter(team__team_id=team_id)
        if squad_players.exists():
            serializer = SquadSerializer(squad_players, many=True)
            return Response(serializer.data)
        return self.get_squad_from_api(team_id)

    def get_squad_from_api(self, team_id):
        url = f'https://v3.football.api-sports.io/players/squads?team={team_id}'
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching squad data: {e}")
            return Response({"error": "Failed to fetch squad data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()
        team_data = data.get('response')[0]
        players = team_data.get('players', [])

        saved_players = []
        for player_data in players:
            player_id = player_data['id']

            # Check if the player exists in the Player model
            try:
                player_instance = Player.objects.get(player_id=player_id)
            except Player.DoesNotExist:
                # Fetch and save the player using PlayerProfileView
                PlayerProfileView().get_player_from_api(player_id)
                try:
                    player_instance = Player.objects.get(player_id=player_id)
                except Player.DoesNotExist:
                    continue  # Skip if still not found

            # Create or update Squad reference for the player and team
            Squad.objects.get_or_create(
                player=player_instance,
                team_id=team_id
            )
            saved_players.append(player_instance)

        # Return the players after ensuring they've been processed
        squad_players = Squad.objects.filter(team__team_id=team_id)
        serializer = SquadSerializer(squad_players, many=True)
        return Response(serializer.data)
  





class PlayerStatView(APIView):
    def get(self, request, player_id, season=None):
        if season is None:
            season = get_year()
        
        try:
            # Try to fetch player statistics for the given player and season
            player_stats = PlayerStat.objects.filter(
                player_id=player_id, 
                season=season
            )
            
            if player_stats.exists():
                serializer = PlayerStatSerializer(player_stats, many=True)
                return Response(serializer.data)
            
            # If no stats exist, fetch and save, then return the data
            self.fetch_and_save_statistics(player_id, season)
            # Query again after saving
            player_stats = PlayerStat.objects.filter(
                player_id=player_id, 
                season=season
            )
            if player_stats.exists():
                serializer = PlayerStatSerializer(player_stats, many=True)
                return Response(serializer.data)
            else:
                return Response({"error": "Player statistics could not be fetched or saved."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return Response({"error": "Failed to retrieve player statistics"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def fetch_and_save_statistics(self, player_id, season):
        # Ensure player exists, fetch if not
        try:
            player = Player.objects.get(player_id=player_id)
        except Player.DoesNotExist:
            PlayerProfileView().get_player_from_api(player_id)
            player = Player.objects.get(player_id=player_id)

        # Fetch player statistics from API
        url = f'https://v3.football.api-sports.io/players?id={player_id}&season={season}'
        
        try:
            response = requests.get(url, headers=accheaders)
            response.raise_for_status()
            data = response.json()

            # Process each statistic entry
            with transaction.atomic():
                for stat_entry in data.get('response', [])[0].get('statistics', []):
                    # Ensure league exists
                    league_id = stat_entry['league']['id']
                    try:
                        league = League.objects.get(league_id=league_id)
                    except League.DoesNotExist:
                        league_response = LeagueView().fetch_league_data_from_api(league_id)
                        league = League.objects.get(league_id=league_id)

                    # Ensure team exists
                    team_id = stat_entry['team']['id']
                    try:
                        team = Team.objects.get(team_id=team_id)
                    except Team.DoesNotExist:
                        TeamIDView().fetch_team_from_api(team_id)
                        team = Team.objects.get(team_id=team_id)

                    # Create or update PlayerStat
                    PlayerStat.objects.update_or_create(
                        player=player,
                        team=team,
                        league=league,
                        season=season,
                        defaults={
                            # Game stats
                            'appearances': stat_entry['games'].get('appearences'),
                            'lineups': stat_entry['games'].get('lineups'),
                            'minutes_played': stat_entry['games'].get('minutes'),
                            'rating': stat_entry['games'].get('rating'),
                            'captain': stat_entry['games'].get('captain', False),

                            # Substitution details
                            'substitutesIn': stat_entry['substitutes'].get('in'),
                            'substitutesOut': stat_entry['substitutes'].get('out'),
                            'bench': stat_entry['substitutes'].get('bench'),

                            # Goal-related stats
                            'assists': stat_entry['goals'].get('assists'),
                            'goalsTotal': stat_entry['goals'].get('total'),
                            'goalsConceded': stat_entry['goals'].get('conceded'),
                            'saves': stat_entry['goals'].get('saves'),

                            # Shooting stats
                            'shotsTotal': stat_entry['shots'].get('total'),
                            'shotsOn': stat_entry['shots'].get('on'),

                            # Passing stats
                            'passTotal': stat_entry['passes'].get('total'),
                            'passKey': stat_entry['passes'].get('key'),
                            'passAccuracy': stat_entry['passes'].get('accuracy'),

                            # Defensive stats
                            'tacklesTotal': stat_entry['tackles'].get('total'),
                            'blocks': stat_entry['tackles'].get('blocks'),
                            'interceptions': stat_entry['tackles'].get('interceptions'),

                            # Duels and dribbling
                            'duelsTotal': stat_entry['duels'].get('total'),
                            'duelsWon': stat_entry['duels'].get('won'),
                            'dribbleAttempts': stat_entry['dribbles'].get('attempts'),
                            'dribbleSuccess': stat_entry['dribbles'].get('success'),
                            'dribblePast': stat_entry['dribbles'].get('past'),

                            # Fouls and cards
                            'foulsDrawn': stat_entry['fouls'].get('drawn'),
                            'foulsCommitted': stat_entry['fouls'].get('committed'),
                            'cardsYellow': stat_entry['cards'].get('yellow'),
                            'cardsYellowRed': stat_entry['cards'].get('yellowred'),
                            'cardsRed': stat_entry['cards'].get('red'),

                            # Penalty stats
                            'penaltyWon': stat_entry['penalty'].get('won'),
                            'penaltyCommited': stat_entry['penalty'].get('commited'),
                            'penaltyScored': stat_entry['penalty'].get('scored'),
                            'penaltyMissed': stat_entry['penalty'].get('missed'),
                            'penaltySaved': stat_entry['penalty'].get('saved')
                        }
                    )

        except Exception as e:
            logger.error(f"Error fetching player statistics: {e}")







class FixtureView(APIView):
    def get(self, request, league_id, season=None):
        # Use current year if season is not provided
        if season is None:
            season = get_year()
        try:
            league = League.objects.get(league_id=league_id)
            season_obj = Season.objects.get(league=league, year=season)
        except League.DoesNotExist:
            return Response({"error": "League not found"}, status=status.HTTP_404_NOT_FOUND)
        except Season.DoesNotExist:
            return Response({"error": "Season not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get fixtures for this league and season
        fixtures = Fixture.objects.filter(league=league, season=season_obj)
        if fixtures.exists():
            serializer = FixtureSerializer(fixtures, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If no fixtures, fetch from API, save, and return
            return self.get_fixtures_from_api(league_id, season)

    def get_fixtures_from_api(self, league_id, season):
        try:
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
            headers = accheaders

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            fixtures_data = response.json()['response']

            # Ensure teams exist
            self.ensure_teams_exist(league_id, season, fixtures_data)

            # Prepare translators
            translator = Translator()

            # Prepare translation collections
            referee_translations = {}
            venue_name_translations = {}
            venue_city_translations = {}
            round_translations = {}

            # Collect unique values for translation
            for fixture in fixtures_data:
                referee = fixture['fixture']['referee']
                if referee:
                    referee_translations[referee] = "The " + str(referee)
                venue_name = fixture['fixture']['venue']['name']
                if venue_name:
                    venue_name_translations[venue_name] = "The " + str(venue_name)
                venue_city = fixture['fixture']['venue']['city']
                if venue_city:
                    venue_city_translations[venue_city] = "The " + str(venue_city)
                round_name = fixture['league']['round']
                if round_name:
                    if 'Regular Season' in round_name:
                        round_name = round_name.replace('Regular Season', 'week')
                    round_translations[round_name] = round_name
                else:
                    round_name = 'Unknown Round'
                    round_translations[round_name] = round_name

            # Bulk translate
            referee_fa_translations = {
                k: translator.translate(v, dest='fa').text 
                for k, v in referee_translations.items()
            } if referee_translations else {}

            venue_name_fa_translations = {
                k: translator.translate(v, dest='fa').text 
                for k, v in venue_name_translations.items()
            } if venue_name_translations else {}

            venue_city_fa_translations = {
                k: translator.translate(v, dest='fa').text 
                for k, v in venue_city_translations.items()
            } if venue_city_translations else {}

            round_fa_translations = {
                k: translator.translate(str(k), dest='fa').text 
                for k in round_translations
            } if round_translations else {}

            # Create fixtures
            fixtures_to_create = []
            for fixture in fixtures_data:
                league_round = fixture['league']['round'] or 'Unknown Round'
                if isinstance(league_round, str) and 'Regular Season' in league_round:
                    league_round = league_round.replace('Regular Season', 'week')

                home_team = Team.objects.get(team_id=fixture['teams']['home']['id'])
                away_team = Team.objects.get(team_id=fixture['teams']['away']['id'])

                fixture_obj = Fixture(
                    league_id=league_id,
                    season_id=Season.objects.get(league_id=league_id, year=season).id,
                    fixture_id=fixture['fixture']['id'],
                    fixture_referee=fixture['fixture']['referee'] or '',
                    fixture_faReferee=referee_fa_translations.get(fixture['fixture']['referee'], ''),
                    fixture_timestamp=fixture['fixture']['timestamp'],
                    fixture_periods_first=fixture['fixture']['periods']['first'],
                    fixture_periods_second=fixture['fixture']['periods']['second'],
                    fixture_venue_name=fixture['fixture']['venue']['name'] or '',
                    fixture_venue_faName=venue_name_fa_translations.get(fixture['fixture']['venue']['name'], ''),
                    fixture_venue_city=fixture['fixture']['venue']['city'] or '',
                    fixture_venue_faCity=venue_city_fa_translations.get(fixture['fixture']['venue']['city'], ''),
                    fixture_status_long=fixture['fixture']['status']['long'],
                    fixture_status_short=fixture['fixture']['status']['short'],
                    fixture_status_elapsed=fixture['fixture']['status']['elapsed'],
                    fixture_status_extra=fixture['fixture']['status']['extra'],
                    league_round=league_round,
                    teams_home=home_team,
                    teams_home_winner=fixture['teams']['home']['winner'],
                    teams_away=away_team,
                    teams_away_winner=fixture['teams']['away']['winner'],
                    goals=fixture['goals'],
                    score_halftime=fixture['score']['halftime'],
                    score_fulltime=fixture['score']['fulltime'],
                    score_extratime=fixture['score']['extratime'],
                    score_penalty=fixture['score']['penalty']
                )
                fixtures_to_create.append(fixture_obj)

            # Bulk create fixtures
            with transaction.atomic():
                Fixture.objects.bulk_create(fixtures_to_create)

                # Create or update FixtureRound
                FixtureRound.objects.update_or_create(
                    league_id=league_id,
                    season_id=Season.objects.get(league_id=league_id, year=season).id,
                    defaults={'rounds': round_fa_translations}
                )

            # Retrieve and serialize fixtures
            fixtures = Fixture.objects.filter(
                league_id=league_id, 
                season__year=season
            )
            serializer = FixtureSerializer(fixtures, many=True)

            return Response({
                'fixtures': serializer.data,
                'rounds': round_fa_translations
            })

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"API request failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def ensure_teams_exist(self, league_id, season, fixtures_data):
        # Collect unique team IDs
        team_ids = set()
        for fixture in fixtures_data:
            team_ids.add(fixture['teams']['home']['id'])
            team_ids.add(fixture['teams']['away']['id'])

        # Check which teams don't exist
        non_existent_teams = [
            team_id for team_id in team_ids 
            if not Team.objects.filter(team_id=team_id).exists()
        ]

        # If there are non-existent teams, fetch them
        if non_existent_teams:
            team_view = TeamView()
            team_view.get_teams_from_api(None, league_id, season)





class FixtureRoundKeysView(APIView):
    def get(self, request, league_id, season=None):
        if season is None:
            season = get_year()
        try:
            league = League.objects.get(league_id=league_id)
            season_obj = Season.objects.get(league=league, year=season)
            try:
                fixture_round = FixtureRound.objects.get(league=league, season=season_obj)
            except FixtureRound.DoesNotExist:
                # Fetch and create fixtures and rounds if not exist
                FixtureView().get_fixtures_from_api(league_id, season)
                fixture_round = FixtureRound.objects.get(league=league, season=season_obj)
            keys = list(fixture_round.rounds.keys())
            return Response({"round_keys": keys}, status=status.HTTP_200_OK)
        except League.DoesNotExist:
            return Response({"error": "League not found"}, status=status.HTTP_404_NOT_FOUND)
        except Season.DoesNotExist:
            return Response({"error": "Season not found"}, status=status.HTTP_404_NOT_FOUND)

class FixtureRoundValuesView(APIView):
    def get(self, request, league_id, season=None):
        if season is None:
            season = get_year()
        try:
            league = League.objects.get(league_id=league_id)
            season_obj = Season.objects.get(league=league, year=season)
            try:
                fixture_round = FixtureRound.objects.get(league=league, season=season_obj)
            except FixtureRound.DoesNotExist:
                # Fetch and create fixtures and rounds if not exist
                FixtureView().get_fixtures_from_api(league_id, season)
                fixture_round = FixtureRound.objects.get(league=league, season=season_obj)
            values = list(fixture_round.rounds.values())
            return Response({"round_values": values}, status=status.HTTP_200_OK)
        except League.DoesNotExist:
            return Response({"error": "League not found"}, status=status.HTTP_404_NOT_FOUND)
        except Season.DoesNotExist:
            return Response({"error": "Season not found"}, status=status.HTTP_404_NOT_FOUND)




class FixtureRoundENView(APIView):
    def get(self, request, league_id, fixture_round, season=None):
        try:
            # If no season provided, use current year
            if season is None:
                season = str(get_year())

            # Ensure league exists
            try:
                league_data = League.objects.get(league_id=league_id)
            except League.DoesNotExist:
                league_response = LeagueView().fetch_league_data_from_api(league_id)
                if league_response.status_code != 200:
                    return league_response
                league_data = League.objects.get(league_id=league_id)

            # Ensure season exists
            try:
                season_data = Season.objects.get(league=league_data, year=season)
            except Season.DoesNotExist:
                return Response(
                    {"error": "Invalid season"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if FixtureRound exists for this league and season
            try:
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data,
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds
            except FixtureRound.DoesNotExist:
                # If no fixture rounds exist, fetch fixtures from API
                fixture_view = FixtureView()
                fixture_response = fixture_view.get_fixtures_from_api(league_id, season)
                # If API fetch fails
                if not isinstance(fixture_response, Response) or fixture_response.status_code != 200:
                    return fixture_response
                # Retry getting fixture rounds
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data,
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds

            # Check if the requested round exists in the rounds dictionary
            if fixture_round not in rounds_dict:
                return Response(
                    {"error": f"Round {fixture_round} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Retrieve fixtures for the specific round
            fixtures = Fixture.objects.filter(
                league=league_data,
                season=season_data,
                league_round=fixture_round
            )

            # If no fixtures found for the specific round
            if not fixtures.exists():
                return Response(
                    {"error": f"No fixtures found for round: {fixture_round}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize and return fixtures
            serializer = FixtureSerializer(fixtures, many=True)

            return Response({
                'fixtures': serializer.data,
                'round': fixture_round
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class FixtureRoundFaView(APIView):
    def get(self, request, league_id, fixture_round_fa, season=None):
        try:
            # If no season provided, use current year
            if season is None:
                season = str(get_year())

            # Use league_id directly, do not look up in myleague_ids
            try:
                league_data = League.objects.get(league_id=league_id)
            except League.DoesNotExist:
                league_response = LeagueView().fetch_league_data_from_api(league_id)
                if league_response.status_code != 200:
                    return league_response
                league_data = League.objects.get(league_id=league_id)

            # Ensure season exists
            try:
                season_data = Season.objects.get(league=league_data, year=season)
            except Season.DoesNotExist:
                return Response(
                    {"error": "Invalid season"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if FixtureRound exists for this league and season
            try:
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data,
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds
            except FixtureRound.DoesNotExist:
                # If no fixture rounds exist, fetch fixtures from API
                fixture_view = FixtureView()
                fixture_response = fixture_view.get_fixtures_from_api(league_id, season)
                # If API fetch fails
                if not isinstance(fixture_response, Response) or fixture_response.status_code != 200:
                    return fixture_response
                # Retry getting fixture rounds
                fixture_rounds = FixtureRound.objects.get(
                    league=league_data,
                    season=season_data
                )
                rounds_dict = fixture_rounds.rounds

            # Find the key corresponding to the provided Persian round name
            fixture_round_key = next((key for key, value in rounds_dict.items() if value == fixture_round_fa), None)

            if fixture_round_key is None:
                return Response(
                    {"error": f"Round '{fixture_round_fa}' not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Retrieve fixtures for the specific round
            fixtures = Fixture.objects.filter(
                league=league_data,
                season=season_data,
                league_round=fixture_round_key
            )

            # If no fixtures found for the specific round
            if not fixtures.exists():
                return Response(
                    {"error": f"No fixtures found for round: {fixture_round_key}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize and return fixtures
            serializer = FixtureSerializer(fixtures, many=True)

            return Response({
                'fixtures': serializer.data,
                'round': fixture_round_key
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FixtureStatView(APIView):
    def get(self, request, fixture_id):
        logger.info(f"Received request for fixture_id: {fixture_id}")

        # Check if statistics already exist for this fixture
        fixture_stats = FixtureStat.objects.filter(fixture__fixture_id=fixture_id)

        if fixture_stats.exists():
            # If statistics exist, serialize and return them
            serializer = FixtureStatSerializer(fixture_stats, many=True)
            logger.info("Returning existing fixture statistics")
            return Response(serializer.data)

        logger.info("Fetching statistics from the API")
        # If statistics do not exist, fetch from the API
        return self.fetch_statistics_from_api(fixture_id)

    def fetch_statistics_from_api(self, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        headers = accheaders  # Ensure accheaders is defined with your API credentials

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json().get('response', [])

            # Prepare to save statistics
            fixture_stats_to_create = []
            for team_stats in data:
                team_id = team_stats['team']['id']
                
                # Create a new FixtureStat instance
                stats = team_stats['statistics']
                fixture_stat = FixtureStat(
                    fixture=Fixture.objects.get(fixture_id=fixture_id),  # Retrieve fixture here
                    team=Team.objects.get(team_id=team_id),
                    ShotsOnGoal=self.get_stat_value(stats, "Shots on Goal"),
                    ShotsOffGoal=self.get_stat_value(stats, "Shots off Goal"),
                    TotalShots=self.get_stat_value(stats, "Total Shots"),
                    BlockedShots=self.get_stat_value(stats, "Blocked Shots"),
                    ShotsInsideBox=self.get_stat_value(stats, "Shots insidebox"),
                    ShotsOutsideBox=self.get_stat_value(stats, "Shots outsidebox"),
                    Fouls=self.get_stat_value(stats, "Fouls"),
                    CornerKicks=self.get_stat_value(stats, "Corner Kicks"),
                    Offsides=self.get_stat_value(stats, "Offsides"),
                    BallPossession=self.get_stat_value(stats, "Ball Possession"),
                    YellowCards=self.get_stat_value(stats, "Yellow Cards"),
                    RedCards=self.get_stat_value(stats, "Red Cards"),
                    GoalkeeperSaves=self.get_stat_value(stats, "Goalkeeper Saves"),
                    Totalpasses=self.get_stat_value(stats, "Total passes"),
                    Passesaccurate=self.get_stat_value(stats, "Passes accurate"),
                    PassesPercent=self.get_stat_value(stats, "Passes %"),
                    ExpectedGoals=self.get_stat_value(stats, "expected_goals"),
                    GoalsPrevented=self.get_stat_value(stats, "goals_prevented"),
                )
                fixture_stats_to_create.append(fixture_stat)

            # Bulk create FixtureStat instances
            FixtureStat.objects.bulk_create(fixture_stats_to_create)

            # Return the newly created statistics
            serializer = FixtureStatSerializer(fixture_stats_to_create, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch fixture statistics: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_stat_value(self, stats, stat_type):
        """Helper method to get the value of a specific statistic type."""
        for stat in stats:
            if stat['type'] == stat_type:
                return stat['value']
        return None




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
                team_obj = Team.objects.get(team_id=event_data['team']['id'])
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
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)




class FixtureLineupView(APIView):
    def get(self, request, fixture_id):
        fixture = get_object_or_404(Fixture, fixture_id=fixture_id)
        fixture_lineups = FixtureLineup.objects.filter(fixture=fixture)
        if fixture_lineups.exists():
            serializer = FixtureLineupSerializer(fixture_lineups, many=True)
            return Response(serializer.data)
        else:
            return self.get_fixture_lineup_from_api(fixture_id)

    def get_fixture_lineup_from_api(self, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            fixture = Fixture.objects.get(fixture_id=fixture_id)
            fixture_lineup_list = []

            for team_data in data['response']:
                team_id = team_data['team']['id']
                coach_id = team_data['coach']['id']

                # Ensure team exists
                team_obj = Team.objects.filter(team_id=team_id).first()
                if not team_obj:
                    TeamIDView().fetch_team_from_api(team_id)
                    team_obj = Team.objects.filter(team_id=team_id).first()
                    if not team_obj:
                        logging.warning(f"Team {team_id} could not be created, skipping lineup.")
                        continue

                # Ensure coach exists
                coach_obj = Coach.objects.filter(coach_id=coach_id).first()
                if not coach_obj:
                    CoachView().get_coach_id_api(coach_id)
                    coach_obj = Coach.objects.filter(coach_id=coach_id).first()

                fixture_lineup_instance, _ = FixtureLineup.objects.get_or_create(
                    fixture=fixture,
                    team=team_obj,
                    defaults={
                        'team_color': team_data['team']['colors'],
                        'coach': coach_obj,
                        'formation': team_data['formation'],
                    }
                )
                fixture_lineup_instance.team_color = team_data['team']['colors']
                fixture_lineup_instance.coach = coach_obj
                fixture_lineup_instance.formation = team_data['formation']
                fixture_lineup_instance.save()

                # Remove old lineup players for this lineup (to avoid duplicates)
                FixtureLineupPlayer.objects.filter(fixture_lineup=fixture_lineup_instance).delete()

                # Save startXI and substitutes
                self.process_players(team_data['startXI'], fixture_lineup_instance, is_starting=True)
                self.process_players(team_data['substitutes'], fixture_lineup_instance, is_starting=False)

                fixture_lineup_list.append(fixture_lineup_instance)

            serializer = FixtureLineupSerializer(fixture_lineup_list, many=True)
            return Response(serializer.data)

        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)

    def process_players(self, players_data, fixture_lineup, is_starting):
        for player_wrap in players_data:
            player_data = player_wrap['player']
            player_id = player_data['id']

            # Ensure player exists
            player_obj = Player.objects.filter(player_id=player_id).first()
            if not player_obj:
                PlayerProfileView().get_player_from_api(player_id)
                player_obj = Player.objects.filter(player_id=player_id).first()
                if not player_obj:
                    logging.warning(f"Player {player_id} could not be created, skipping.")
                    continue  # Skip if still not found

            # Map and update position if needed
            pos_short = player_data.get('pos')
            if pos_short:
                player_obj.position = Player.POS_MAP.get(pos_short, None)
                player_obj.save()

            FixtureLineupPlayer.objects.create(
                fixture_lineup=fixture_lineup,
                player=player_obj,
                is_starting=is_starting,
                pos=pos_short,
                grid=player_data.get('grid'),
                number=player_data.get('number'),
            )
            logging.info(f"Added player {player_obj.name} to lineup {fixture_lineup.id} (is_starting={is_starting})")

class FixturePlayerView(APIView):
    def get(self, request, fixture_id):
        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        fixture_players = FixturePlayer.objects.filter(fixture=fixture)
        if fixture_players.exists():
            serializer = FixturePlayerSerializer(fixture_players, many=True)
            return Response(serializer.data)
        else:
            return self.fetch_players_from_api(fixture_id)

    def fetch_players_from_api(self, fixture_id):
        url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture_id}"
        headers = accheaders

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture not found"}, status=404)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get('response', [])
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to fetch fixture player data: {e}"}, status=500)

        players_to_create = []
        for team_data in data:
            team_id = team_data['team']['id']
            try:
                team_obj = Team.objects.get(team_id=team_id)
            except Team.DoesNotExist:
                TeamIDView().fetch_team_from_api(team_id)
                team_obj = Team.objects.filter(team_id=team_id).first()
                if not team_obj:
                    continue

            for player_entry in team_data['players']:
                player_info = player_entry['player']
                player_id = player_info['id']

                # Ensure player exists
                player_obj = Player.objects.filter(player_id=player_id).first()
                if not player_obj:
                    PlayerProfileView().get_player_from_api(player_id)
                    player_obj = Player.objects.filter(player_id=player_id).first()
                    if not player_obj:
                        continue

                stats = player_entry['statistics'][0] if player_entry['statistics'] else {}

                games = stats.get('games', {})
                shots = stats.get('shots', {})
                goals = stats.get('goals', {})
                passes = stats.get('passes', {})
                tackles = stats.get('tackles', {})
                duels = stats.get('duels', {})
                dribbles = stats.get('dribbles', {})
                fouls = stats.get('fouls', {})
                cards = stats.get('cards', {})
                penalty = stats.get('penalty', {})

                # Update or create FixturePlayer
                fp, _ = FixturePlayer.objects.update_or_create(
                    fixture=fixture,
                    team=team_obj,
                    player=player_obj,
                    defaults={
                        'minutes': games.get('minutes'),
                        'rating': float(games.get('rating')) if games.get('rating') else None,
                        'captain': games.get('captain', False),
                        'substitute': games.get('substitute', False),
                        'number': games.get('number'),
                        'position': games.get('position'),
                        'offsides': stats.get('offsides'),
                        'shots_total': shots.get('total'),
                        'shots_on': shots.get('on'),
                        'goals_total': goals.get('total'),
                        'goals_conceded': goals.get('conceded'),
                        'assists': goals.get('assists'),
                        'saves': goals.get('saves'),
                        'passes_total': passes.get('total'),
                        'passes_key': passes.get('key'),
                        'passes_accuracy': passes.get('accuracy'),
                        'tackles_total': tackles.get('total'),
                        'blocks': tackles.get('blocks'),
                        'interceptions': tackles.get('interceptions'),
                        'duels_total': duels.get('total'),
                        'duels_won': duels.get('won'),
                        'dribbles_attempts': dribbles.get('attempts'),
                        'dribbles_success': dribbles.get('success'),
                        'dribbles_past': dribbles.get('past'),
                        'fouls_drawn': fouls.get('drawn'),
                        'fouls_committed': fouls.get('committed'),
                        'cards_yellow': cards.get('yellow'),
                        'cards_red': cards.get('red'),
                        'penalty_won': penalty.get('won'),
                        'penalty_commited': penalty.get('commited'),
                        'penalty_scored': penalty.get('scored'),
                        'penalty_missed': penalty.get('missed'),
                        'penalty_saved': penalty.get('saved'),
                    }
                )
                players_to_create.append(fp)

        serializer = FixturePlayerSerializer(players_to_create, many=True)
        return Response(serializer.data, status=201)






class FixtureH2H(APIView):
    def get(self, request, fixture_id):
        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id)
            home_team_id = fixture.teams_home.team_id
            away_team_id = fixture.teams_away.team_id

            fixtures = Fixture.objects.filter(
                (Q(teams_home_id=home_team_id) & Q(teams_away_id=away_team_id)) |
                (Q(teams_home_id=away_team_id) & Q(teams_away_id=home_team_id)),
                fixture_status_short="FT"
            ).order_by('-fixture_timestamp')

            if len(fixtures) < 3:
                return self.fetch_h2h_from_api(home_team_id, away_team_id)

            final_summary, league_stats = self.calculate_summary(fixtures, fixture)
            serializer = FixtureH2HSerializer(fixtures, many=True)
            response_data = {
                "summary": final_summary,
                "fixtures": serializer.data
            }
            return Response(response_data)

        except Fixture.DoesNotExist:
            return Response({"error": "Fixture does not exist"}, status=404)

    def fetch_h2h_from_api(self, home_team_id, away_team_id):
        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={home_team_id}-{away_team_id}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()['response']

            fixtures_list = []
            for fixture_data in data:
                league_id = fixture_data['league']['id']
                season_year = fixture_data['league']['season']

                # Ensure league exists
                league = League.objects.filter(league_id=league_id).first()
                if not league:
                    LeagueView().fetch_league_data_from_api(league_id)
                    league = League.objects.filter(league_id=league_id).first()
                    if not league:
                        continue  # Skip if still not found

                # Ensure season exists
                season, _ = Season.objects.get_or_create(
                    league=league,
                    year=season_year,
                )

                # Ensure teams exist
                home_id = fixture_data['teams']['home']['id']
                away_id = fixture_data['teams']['away']['id']
                for team_id in [home_id, away_id]:
                    if not Team.objects.filter(team_id=team_id).exists():
                        TeamIDView().fetch_team_from_api(team_id)

                # Create or update fixture
                fixture_obj, _ = Fixture.objects.update_or_create(
                    fixture_id=fixture_data['fixture']['id'],
                    defaults={
                        'league': league,
                        'season': season,
                        'teams_home_id': home_id,
                        'teams_away_id': away_id,
                        'goals': fixture_data['goals'],
                        'score_halftime': fixture_data['score']['halftime'],
                        'score_fulltime': fixture_data['score']['fulltime'],
                        'score_extratime': fixture_data['score']['extratime'],
                        'score_penalty': fixture_data['score']['penalty'],
                        'fixture_referee': fixture_data['fixture']['referee'],
                        'fixture_timestamp': fixture_data['fixture']['timestamp'],
                        'fixture_periods_first': fixture_data['fixture']['periods']['first'],
                        'fixture_periods_second': fixture_data['fixture']['periods']['second'],
                        'fixture_venue_name': fixture_data['fixture']['venue']['name'],
                        'fixture_venue_city': fixture_data['fixture']['venue']['city'],
                        'fixture_status_long': fixture_data['fixture']['status']['long'],
                        'fixture_status_short': fixture_data['fixture']['status']['short'],
                        'fixture_status_elapsed': fixture_data['fixture']['status']['elapsed'],
                    }
                )
                fixtures_list.append(fixture_obj)

            fixtures_list.sort(key=lambda x: x.fixture_timestamp, reverse=True)
            if not fixtures_list:
                return Response({"error": "No H2H fixtures found."}, status=404)

            final_summary, league_stats = self.calculate_summary(fixtures_list, fixtures_list[0])
            serializer = FixtureH2HSerializer(fixtures_list, many=True)
            response_data = {
                "summary": final_summary,
                "fixtures": serializer.data
            }
            return Response(response_data)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch head-to-head data: " + str(e)}, status=500)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=500)

    def calculate_summary(self, fixtures, fixture):
        summary = {
            "total_fixtures": len(fixtures),
            "total_goals": 0,
            "draws": 0,
            f"{fixture.teams_home.team_name} goals": 0,
            f"{fixture.teams_away.team_name} goals": 0,
            f"{fixture.teams_home.team_name} wins": 0,
            f"{fixture.teams_away.team_name} wins": 0,
        }
        league_stats = {}

        for fixture in fixtures:
            home_goals = fixture.score_fulltime.get('home', 0) or 0
            away_goals = fixture.score_fulltime.get('away', 0) or 0

            summary["total_goals"] += home_goals + away_goals
            summary[f"{fixture.teams_home.team_name} goals"] += home_goals
            summary[f"{fixture.teams_away.team_name} goals"] += away_goals

            if home_goals > away_goals:
                summary[f"{fixture.teams_home.team_name} wins"] += 1
            elif away_goals > home_goals:
                summary[f"{fixture.teams_away.team_name} wins"] += 1
            else:
                summary["draws"] += 1

            league_id = fixture.league.league_id
            if league_id not in league_stats:
                league_stats[league_id] = {
                    "total_fixtures": 0,
                    "total_goals": 0,
                    f"{fixture.teams_home.team_name} goals": 0,
                    f"{fixture.teams_away.team_name} goals": 0,
                    f"{fixture.teams_home.team_name} wins": 0,
                    f"{fixture.teams_away.team_name} wins": 0,
                    "draws": 0,
                }

            league_stats[league_id]["total_fixtures"] += 1
            league_stats[league_id]["total_goals"] += home_goals + away_goals
            league_stats[league_id][f"{fixture.teams_home.team_name} goals"] += home_goals
            league_stats[league_id][f"{fixture.teams_away.team_name} goals"] += away_goals

            if home_goals > away_goals:
                league_stats[league_id][f"{fixture.teams_home.team_name} wins"] += 1
            elif away_goals > home_goals:
                league_stats[league_id][f"{fixture.teams_away.team_name} wins"] += 1
            else:
                league_stats[league_id]["draws"] += 1

        final_summary = {
            "total_fixtures": summary["total_fixtures"],
            "total_goals": summary["total_goals"],
            "draws": summary["draws"],
            f"{fixture.teams_home.team_name} goals": summary[f"{fixture.teams_home.team_name} goals"],
            f"{fixture.teams_away.team_name} goals": summary[f"{fixture.teams_away.team_name} goals"],
            f"{fixture.teams_home.team_name} wins": summary[f"{fixture.teams_home.team_name} wins"],
            f"{fixture.teams_away.team_name} wins": summary[f"{fixture.teams_away.team_name} wins"],
        }

        for league_id, stats in league_stats.items():
            final_summary[f"league_{league_id}"] = stats

        return final_summary, league_stats
    







    
class FixtureDateView(APIView):
    def get(self, request, date=None):
        if date is None:
            date = get_today_date()  # e.g., "2024-06-14"
        try:
            start_timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except Exception:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        end_timestamp = start_timestamp + 86400

        fixtures = Fixture.objects.filter(
            fixture_timestamp__gte=start_timestamp,
            fixture_timestamp__lt=end_timestamp
        ).order_by('fixture_timestamp')

        if fixtures.exists():
            serializer = FixtureSerializer(fixtures, many=True)
            return Response(serializer.data)
        else:
            return self.fetch_fixtures_date(date)

    def fetch_fixtures_date(self, date):
        url = f"https://v3.football.api-sports.io/fixtures?date={date}"
        headers = accheaders

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            fixtures_data = response.json().get('response', [])
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to fetch fixtures from API: {e}"}, status=500)

        saved_fixtures = []
        for fixture_data in fixtures_data:
            league_id = fixture_data['league']['id']

            # Only process leagues in myleague_ids
            if league_id not in myleague_ids.values():
                continue

            # Ensure League exists
            league = League.objects.filter(league_id=league_id).first()
            if not league:
                LeagueView().fetch_league_data_from_api(league_id)
                league = League.objects.filter(league_id=league_id).first()
                if not league:
                    continue

            # Ensure Season exists
            season_year = fixture_data['league']['season']
            season, _ = Season.objects.get_or_create(league=league, year=season_year)

            # Ensure Teams exist
            home_team_id = fixture_data['teams']['home']['id']
            away_team_id = fixture_data['teams']['away']['id']
            for team_id in [home_team_id, away_team_id]:
                if not Team.objects.filter(team_id=team_id).exists():
                    TeamIDView().fetch_team_from_api(team_id)

            home_team = Team.objects.filter(team_id=home_team_id).first()
            away_team = Team.objects.filter(team_id=away_team_id).first()
            if not home_team or not away_team:
                continue

            # Venue info (handle missing keys)
            venue_data = fixture_data['fixture'].get('venue', {})
            venue_name = venue_data.get('name', '')
            venue_city = venue_data.get('city', '')

            # Create or update Fixture
            fixture_obj, _ = Fixture.objects.update_or_create(
                fixture_id=fixture_data['fixture']['id'],
                defaults={
                    'league': league,
                    'season': season,
                    'teams_home': home_team,
                    'teams_away': away_team,
                    'fixture_referee': fixture_data['fixture'].get('referee'),
                    'fixture_timestamp': fixture_data['fixture'].get('timestamp'),
                    'fixture_periods_first': fixture_data['fixture'].get('periods', {}).get('first'),
                    'fixture_periods_second': fixture_data['fixture'].get('periods', {}).get('second'),
                    'fixture_venue_name': venue_name,
                    'fixture_venue_city': venue_city,
                    'fixture_status_long': fixture_data['fixture'].get('status', {}).get('long'),
                    'fixture_status_short': fixture_data['fixture'].get('status', {}).get('short'),
                    'fixture_status_elapsed': fixture_data['fixture'].get('status', {}).get('elapsed'),
                    'goals': fixture_data.get('goals', {}),
                    'score_halftime': fixture_data.get('score', {}).get('halftime'),
                    'score_fulltime': fixture_data.get('score', {}).get('fulltime'),
                    'score_extratime': fixture_data.get('score', {}).get('extratime'),
                    'score_penalty': fixture_data.get('score', {}).get('penalty'),
                }
            )
            saved_fixtures.append(fixture_obj)

        # Return all fixtures for this date from DB (sorted)
        start_timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        end_timestamp = start_timestamp + 86400
        fixtures = Fixture.objects.filter(
            fixture_timestamp__gte=start_timestamp,
            fixture_timestamp__lt=end_timestamp
        ).order_by('fixture_timestamp')
        serializer = FixtureSerializer(fixtures, many=True)
        return Response(serializer.data)





class TableView(APIView):
    def get(self, request, league_id, season=None):
        try:
            league = League.objects.get(league_id=league_id)
        except League.DoesNotExist:
            return Response({"error": "League not found"}, status=status.HTTP_404_NOT_FOUND)

        if season is not None:
            try:
                season_obj = Season.objects.get(league=league, year=season)
            except Season.DoesNotExist:
                return Response({"error": "Season not found"}, status=status.HTTP_404_NOT_FOUND)
            tables = Table.objects.filter(league=league, season=season_obj).order_by('rank')
        else:
            tables = Table.objects.filter(league=league).order_by('season__year', 'rank')

        if tables.exists():
            serializer = TableSerializer(tables, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif season is not None:
            # If no table data, fetch from API and return
            return self.get_table_from_api(league_id, season)
        else:
            return Response({"error": "No table data found and no season provided to fetch from API."}, status=status.HTTP_404_NOT_FOUND)
    
    def get_table_from_api(self, league_id, season):
        url = f'https://v3.football.api-sports.io/standings?league={league_id}&season={season}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()  # Get the full response
            # Check if 'response' key exists
            if 'response' not in data or not data['response']:
                return Response({"error": "No data found in response"}, status=status.HTTP_404_NOT_FOUND)

            # Iterate through each league data in the response
            for league_data in data['response']:
                standings = league_data['league']['standings']  # Get the standings for this league

                with transaction.atomic():
                    for group_standings in standings:  # Iterate through each group of standings
                        for entry in group_standings:  # Iterate through each entry in the group
                            team_id = entry['team']['id']
                            
                            # Check if team exists
                            if not Team.objects.filter(team_id=team_id).exists():
                                # If team does not exist, fetch teams
                                TeamView().get_teams_from_api(None, league_id, season)

                            # Now that we are sure the team exists, save the table entry
                            team = Team.objects.get(team_id=team_id)
                            table_entry = Table(
                                league=League.objects.get(league_id=league_id),
                                season=Season.objects.get(league_id=league_id, year=season),
                                team=team,
                                rank=entry['rank'],
                                points=entry['points'],
                                goals_diff=entry['goalsDiff'],
                                group=entry['group'],
                                form=entry['form'],
                                status=entry['status'],
                                description=entry.get('description', ''),  # Handle potential null values
                                played=entry['all']['played'],
                                win=entry['all']['win'],
                                draw=entry['all']['draw'],
                                lose=entry['all']['lose'],
                                goals_for=entry['all']['goals']['for'],
                                goals_against=entry['all']['goals']['against'],
                                last_update=entry['update']
                            )
                            table_entry.save()

            # Return the newly created table data
            table_data = Table.objects.filter(league_id=league_id, season__year=season)
            serializer = TableSerializer(table_data, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch table data: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class TopScoreView(APIView):
    
    def get(self, request, league_id, season=None):
        # Set default season if not provided
        if season is None:
            season = str(get_year())
        else:
            season = str(season)  # Ensure season is a string

        # Fetch top scorers from the database
        top_scorers = PlayerStat.objects.filter(
            league__league_id=league_id,  # Filter by league ID
            season=season  # Filter by season (now an integer)
        ).order_by('-goalsTotal')[:20]  # Assuming 'goalsTotal' is a field in PlayerStat

        if top_scorers.exists():
            serializer = TopScoreSerializer(top_scorers, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No top scorers found for the given league and season."}, status=status.HTTP_404_NOT_FOUND)

    
    def get_or_update_top_scorers(self, league_id, season=None):
        if season is None:
            season = str(get_year())  # Set default season if not provided
        url = f'https://v3.football.api-sports.io/players/topscorers?league={league_id}&season={season}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            if 'response' not in data or not data['response']:
                return Response({"error": "No top scorer data found."}, status=status.HTTP_404_NOT_FOUND)

            # Process each player in the response
            for player_data in data['response']:
                player_id = player_data['player']['id']
                
                # Check if the player exists in the Player model
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    # If player does not exist, fetch and save player data
                    PlayerProfileView().get_player_from_api(player_id)

                # Ensure player_instance is valid before proceeding
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    return Response({"error": f"Player with ID {player_id} could not be created."}, status=status.HTTP_400_BAD_REQUEST)

                # Access statistics (assuming it's a list and we take the first entry)
                statistics = player_data['statistics']
                if not statistics:
                    continue  # Skip if no statistics are available

                for stat in statistics:
                    team_id = stat['team']['id']
                    league_id = stat['league']['id']
                    season_year = stat['league']['season']

                    # Check if the league exists
                    league_instance = League.objects.filter(league_id=league_id).first()
                    if not league_instance:
                        LeagueView().fetch_league_data_from_api(league_id)

                    # Check if the team exists
                    team_instance = Team.objects.filter(team_id=team_id).first()
                    if not team_instance:
                        TeamIDView().fetch_team_from_api(team_id)

                    # Create or update the PlayerStat instance
                    player_stat, created = PlayerStat.objects.update_or_create(
                        player=player_instance,
                        team=team_instance,
                        league=league_instance,
                        season=season_year,  # Save the season as an integer
                        defaults={
                            'appearances': stat['games'].get('appearances', 0),
                            'lineups': stat['games'].get('lineups', 0),
                            'assists': stat['goals'].get('assists', 0),
                            'minutes_played': stat['games'].get('minutes', 0),
                            'rating': stat.get('rating', None),
                            'captain': stat.get('captain', False),
                            'substitutesIn': stat['substitutes'].get('in', 0),
                            'substitutesOut': stat['substitutes'].get('out', 0),
                            'bench': stat['substitutes'].get('bench', 0),
                            'shotsTotal': stat['shots'].get('total', 0),
                            'shotsOn': stat['shots'].get('on', 0),
                            'goalsTotal': stat['goals'].get('total', 0),
                            'goalsConceded': stat['goals'].get('conceded', 0),
                            'saves': stat['goals'].get('saves', 0),
                            'passTotal': stat['passes'].get('total', 0),
                            'passKey': stat['passes'].get('key', 0),
                            'passAccuracy': stat['passes'].get('accuracy', 0.0),
                            'tacklesTotal': stat['tackles'].get('total', 0),
                            'blocks': stat['tackles'].get('blocks', 0),
                            'interceptions': stat['tackles'].get('interceptions', 0),
                            'duelsTotal': stat['duels'].get('total', 0),
                            'duelsWon': stat['duels'].get('won', 0),
                            'dribbleAttempts': stat['dribbles'].get('attempts', 0),
                            'dribbleSuccess': stat['dribbles'].get('success', 0),
                            'dribblePast': stat['dribbles'].get('past', 0),
                            'foulsDrawn': stat['fouls'].get('drawn', 0),
                            'foulsCommitted': stat['fouls'].get('committed', 0),
                            'cardsYellow': stat['cards'].get('yellow', 0),
                            'cardsYellowRed': stat['cards'].get('yellowred', 0),
                            'cardsRed': stat['cards'].get('red', 0),
                            'penaltyWon': stat['penalty'].get('won', 0),
                            'penaltyCommited': stat['penalty'].get('commited', 0),
                            'penaltyScored': stat['penalty'].get('scored', 0),
                            'penaltyMissed': stat['penalty'].get('missed', 0),
                            'penaltySaved': stat['penalty'].get('saved', 0),
                        }
                    )

            return Response({"message": "Top scorers updated successfully."}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching top scorers: {e}")
            return Response({"error": "Failed to fetch top scorers."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class TopAssistView(APIView):
    def get(self, request, league_id, season=None):
        # Set default season if not provided
        if season is None:
            season = str(get_year())
        else:
            season = str(season)  # Ensure season is a string

        # Fetch top Assists from the database
        top_assists = PlayerStat.objects.filter(
            league__league_id=league_id,  # Filter by league ID
            season=season  # Filter by season (now an integer)
        ).order_by('-assists')[:20]  # Assuming 'assists' is a field in PlayerStat

        if top_assists.exists():
            serializer = TopAssistSerializer(top_assists, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No top assists found for the given league and season."}, status=status.HTTP_404_NOT_FOUND)

    
    def get_or_update_top_assists(self, league_id, season=None):
        if season is None:
            season = str(get_year())  # Set default season if not provided
        url = f'https://v3.football.api-sports.io/players/topassists?league={league_id}&season={season}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            if 'response' not in data or not data['response']:
                return Response({"error": "No top assist data found."}, status=status.HTTP_404_NOT_FOUND)

            # Process each player in the response
            for player_data in data['response']:
                player_id = player_data['player']['id']
                
                # Check if the player exists in the Player model
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    # If player does not exist, fetch and save player data
                    PlayerProfileView().get_player_from_api(player_id)

                # Ensure player_instance is valid before proceeding
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    return Response({"error": f"Player with ID {player_id} could not be created."}, status=status.HTTP_400_BAD_REQUEST)

                # Access statistics (assuming it's a list and we take the first entry)
                statistics = player_data['statistics']
                if not statistics:
                    continue  # Skip if no statistics are available

                for stat in statistics:
                    team_id = stat['team']['id']
                    league_id = stat['league']['id']
                    season_year = stat['league']['season']

                    # Check if the league exists
                    league_instance = League.objects.filter(league_id=league_id).first()
                    if not league_instance:
                        LeagueView().fetch_league_data_from_api(league_id)

                    # Check if the team exists
                    team_instance = Team.objects.filter(team_id=team_id).first()
                    if not team_instance:
                        TeamIDView().fetch_team_from_api(team_id)

                    # Create or update the PlayerStat instance
                    player_stat, created = PlayerStat.objects.update_or_create(
                        player=player_instance,
                        team=team_instance,
                        league=league_instance,
                        season=season_year,  # Save the season as an integer
                        defaults={
                            'appearances': stat['games'].get('appearances', 0),
                            'lineups': stat['games'].get('lineups', 0),
                            'assists': stat['goals'].get('assists', 0),
                            'minutes_played': stat['games'].get('minutes', 0),
                            'rating': stat.get('rating', None),
                            'captain': stat.get('captain', False),
                            'substitutesIn': stat['substitutes'].get('in', 0),
                            'substitutesOut': stat['substitutes'].get('out', 0),
                            'bench': stat['substitutes'].get('bench', 0),
                            'shotsTotal': stat['shots'].get('total', 0),
                            'shotsOn': stat['shots'].get('on', 0),
                            'goalsTotal': stat['goals'].get('total', 0),
                            'goalsConceded': stat['goals'].get('conceded', 0),
                            'saves': stat['goals'].get('saves', 0),
                            'passTotal': stat['passes'].get('total', 0),
                            'passKey': stat['passes'].get('key', 0),
                            'passAccuracy': stat['passes'].get('accuracy', 0.0),
                            'tacklesTotal': stat['tackles'].get('total', 0),
                            'blocks': stat['tackles'].get('blocks', 0),
                            'interceptions': stat['tackles'].get('interceptions', 0),
                            'duelsTotal': stat['duels'].get('total', 0),
                            'duelsWon': stat['duels'].get('won', 0),
                            'dribbleAttempts': stat['dribbles'].get('attempts', 0),
                            'dribbleSuccess': stat['dribbles'].get('success', 0),
                            'dribblePast': stat['dribbles'].get('past', 0),
                            'foulsDrawn': stat['fouls'].get('drawn', 0),
                            'foulsCommitted': stat['fouls'].get('committed', 0),
                            'cardsYellow': stat['cards'].get('yellow', 0),
                            'cardsYellowRed': stat['cards'].get('yellowred', 0),
                            'cardsRed': stat['cards'].get('red', 0),
                            'penaltyWon': stat['penalty'].get('won', 0),
                            'penaltyCommited': stat['penalty'].get('commited', 0),
                            'penaltyScored': stat['penalty'].get('scored', 0),
                            'penaltyMissed': stat['penalty'].get('missed', 0),
                            'penaltySaved': stat['penalty'].get('saved', 0),
                        }
                    )

            return Response({"message": "Top assists updated successfully."}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching top assists: {e}")
            return Response({"error": "Failed to fetch top scorers."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class TopYellowCardView(APIView):
    def get(self, request, league_id, season=None):
        # Set default season if not provided
        if season is None:
            season = str(get_year())
        else:
            season = str(season)  # Ensure season is a string

        # Fetch top yellow from the database
        top_yellow = PlayerStat.objects.filter(
            league__league_id=league_id,  # Filter by league ID
            season=season  # Filter by season (now an integer)
        ).order_by('-cardsYellow')[:20]  # Assuming 'cardsYellow' is a field in PlayerStat

        if top_yellow.exists():
            serializer = TopYellowCardSerializer(top_yellow, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No top yellow found for the given league and season."}, status=status.HTTP_404_NOT_FOUND)

    
    def get_or_update_top_yellow(self, league_id, season=None):
        if season is None:
            season = str(get_year())  # Set default season if not provided
        url = f'https://v3.football.api-sports.io/players/topyellowcards?league={league_id}&season={season}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            if 'response' not in data or not data['response']:
                return Response({"error": "No top assist data found."}, status=status.HTTP_404_NOT_FOUND)

            # Process each player in the response
            for player_data in data['response']:
                player_id = player_data['player']['id']
                
                # Check if the player exists in the Player model
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    # If player does not exist, fetch and save player data
                    PlayerProfileView().get_player_from_api(player_id)

                # Ensure player_instance is valid before proceeding
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    return Response({"error": f"Player with ID {player_id} could not be created."}, status=status.HTTP_400_BAD_REQUEST)

                # Access statistics (assuming it's a list and we take the first entry)
                statistics = player_data['statistics']
                if not statistics:
                    continue  # Skip if no statistics are available

                for stat in statistics:
                    team_id = stat['team']['id']
                    league_id = stat['league']['id']
                    season_year = stat['league']['season']

                    # Check if the league exists
                    league_instance = League.objects.filter(league_id=league_id).first()
                    if not league_instance:
                        LeagueView().fetch_league_data_from_api(league_id)

                    # Check if the team exists
                    team_instance = Team.objects.filter(team_id=team_id).first()
                    if not team_instance:
                        TeamIDView().fetch_team_from_api(team_id)

                    # Create or update the PlayerStat instance
                    player_stat, created = PlayerStat.objects.update_or_create(
                        player=player_instance,
                        team=team_instance,
                        league=league_instance,
                        season=season_year,  # Save the season as an integer
                        defaults={
                            'appearances': stat['games'].get('appearances', 0),
                            'lineups': stat['games'].get('lineups', 0),
                            'assists': stat['goals'].get('assists', 0),
                            'minutes_played': stat['games'].get('minutes', 0),
                            'rating': stat.get('rating', None),
                            'captain': stat.get('captain', False),
                            'substitutesIn': stat['substitutes'].get('in', 0),
                            'substitutesOut': stat['substitutes'].get('out', 0),
                            'bench': stat['substitutes'].get('bench', 0),
                            'shotsTotal': stat['shots'].get('total', 0),
                            'shotsOn': stat['shots'].get('on', 0),
                            'goalsTotal': stat['goals'].get('total', 0),
                            'goalsConceded': stat['goals'].get('conceded', 0),
                            'saves': stat['goals'].get('saves', 0),
                            'passTotal': stat['passes'].get('total', 0),
                            'passKey': stat['passes'].get('key', 0),
                            'passAccuracy': stat['passes'].get('accuracy', 0.0),
                            'tacklesTotal': stat['tackles'].get('total', 0),
                            'blocks': stat['tackles'].get('blocks', 0),
                            'interceptions': stat['tackles'].get('interceptions', 0),
                            'duelsTotal': stat['duels'].get('total', 0),
                            'duelsWon': stat['duels'].get('won', 0),
                            'dribbleAttempts': stat['dribbles'].get('attempts', 0),
                            'dribbleSuccess': stat['dribbles'].get('success', 0),
                            'dribblePast': stat['dribbles'].get('past', 0),
                            'foulsDrawn': stat['fouls'].get('drawn', 0),
                            'foulsCommitted': stat['fouls'].get('committed', 0),
                            'cardsYellow': stat['cards'].get('yellow', 0),
                            'cardsYellowRed': stat['cards'].get('yellowred', 0),
                            'cardsRed': stat['cards'].get('red', 0),
                            'penaltyWon': stat['penalty'].get('won', 0),
                            'penaltyCommited': stat['penalty'].get('commited', 0),
                            'penaltyScored': stat['penalty'].get('scored', 0),
                            'penaltyMissed': stat['penalty'].get('missed', 0),
                            'penaltySaved': stat['penalty'].get('saved', 0),
                        }
                    )

            return Response({"message": "Top yellow cards updated successfully."}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching top yellow cards: {e}")
            return Response({"error": "Failed to fetch top scorers."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








class TopRedCardView(APIView):
    def get(self, request, league_id, season=None):
        # Set default season if not provided
        if season is None:
            season = str(get_year())
        else:
            season = str(season)  # Ensure season is a string

        # Fetch top red from the database
        top_red = PlayerStat.objects.filter(
            league__league_id=league_id,  # Filter by league ID
            season=season  # Filter by season (now an integer)
        ).order_by('-cardsRed')[:20]  # Assuming 'cardsred' is a field in PlayerStat

        if top_red.exists():
            serializer = TopRedCardSerializer(top_red, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No top red found for the given league and season."}, status=status.HTTP_404_NOT_FOUND)

    
    def get_or_update_top_red(self, league_id, season=None):
        if season is None:
            season = str(get_year())  # Set default season if not provided
        url = f'https://v3.football.api-sports.io/players/topredcards?league={league_id}&season={season}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            if 'response' not in data or not data['response']:
                return Response({"error": "No top assist data found."}, status=status.HTTP_404_NOT_FOUND)

            # Process each player in the response
            for player_data in data['response']:
                player_id = player_data['player']['id']
                
                # Check if the player exists in the Player model
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    # If player does not exist, fetch and save player data
                    PlayerProfileView().get_player_from_api(player_id)

                # Ensure player_instance is valid before proceeding
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    return Response({"error": f"Player with ID {player_id} could not be created."}, status=status.HTTP_400_BAD_REQUEST)

                # Access statistics (assuming it's a list and we take the first entry)
                statistics = player_data['statistics']
                if not statistics:
                    continue  # Skip if no statistics are available

                for stat in statistics:
                    team_id = stat['team']['id']
                    league_id = stat['league']['id']
                    season_year = stat['league']['season']

                    # Check if the league exists
                    league_instance = League.objects.filter(league_id=league_id).first()
                    if not league_instance:
                        LeagueView().fetch_league_data_from_api(league_id)

                    # Check if the team exists
                    team_instance = Team.objects.filter(team_id=team_id).first()
                    if not team_instance:
                        TeamIDView().fetch_team_from_api(team_id)

                    # Create or update the PlayerStat instance
                    player_stat, created = PlayerStat.objects.update_or_create(
                        player=player_instance,
                        team=team_instance,
                        league=league_instance,
                        season=season_year,  # Save the season as an integer
                        defaults={
                            'appearances': stat['games'].get('appearances', 0),
                            'lineups': stat['games'].get('lineups', 0),
                            'assists': stat['goals'].get('assists', 0),
                            'minutes_played': stat['games'].get('minutes', 0),
                            'rating': stat.get('rating', None),
                            'captain': stat.get('captain', False),
                            'substitutesIn': stat['substitutes'].get('in', 0),
                            'substitutesOut': stat['substitutes'].get('out', 0),
                            'bench': stat['substitutes'].get('bench', 0),
                            'shotsTotal': stat['shots'].get('total', 0),
                            'shotsOn': stat['shots'].get('on', 0),
                            'goalsTotal': stat['goals'].get('total', 0),
                            'goalsConceded': stat['goals'].get('conceded', 0),
                            'saves': stat['goals'].get('saves', 0),
                            'passTotal': stat['passes'].get('total', 0),
                            'passKey': stat['passes'].get('key', 0),
                            'passAccuracy': stat['passes'].get('accuracy', 0.0),
                            'tacklesTotal': stat['tackles'].get('total', 0),
                            'blocks': stat['tackles'].get('blocks', 0),
                            'interceptions': stat['tackles'].get('interceptions', 0),
                            'duelsTotal': stat['duels'].get('total', 0),
                            'duelsWon': stat['duels'].get('won', 0),
                            'dribbleAttempts': stat['dribbles'].get('attempts', 0),
                            'dribbleSuccess': stat['dribbles'].get('success', 0),
                            'dribblePast': stat['dribbles'].get('past', 0),
                            'foulsDrawn': stat['fouls'].get('drawn', 0),
                            'foulsCommitted': stat['fouls'].get('committed', 0),
                            'cardsYellow': stat['cards'].get('yellow', 0),
                            'cardsYellowRed': stat['cards'].get('yellowred', 0),
                            'cardsRed': stat['cards'].get('red', 0),
                            'penaltyWon': stat['penalty'].get('won', 0),
                            'penaltyCommited': stat['penalty'].get('commited', 0),
                            'penaltyScored': stat['penalty'].get('scored', 0),
                            'penaltyMissed': stat['penalty'].get('missed', 0),
                            'penaltySaved': stat['penalty'].get('saved', 0),
                        }
                    )

            return Response({"message": "Top red cards updated successfully."}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching top red cards: {e}")
            return Response({"error": "Failed to fetch top scorers."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TransfersTeamInView(APIView):
    def get(self, request, team_id):
        # Filter transfers where team_in matches the provided team_id and exclude transfers with transfer_type "Loan"
        transfers = Transfer.objects.filter(team_in__team_id=team_id).exclude(transfer_type="Loan").order_by('-transfer_date')
        
        if transfers.exists():
            serializer = TransferSerializer(transfers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "No transfers found for this team."}, status=status.HTTP_404_NOT_FOUND)

    
    def get_team_transfers_from_api(self, team_id):
        url = f'https://v3.football.api-sports.io/transfers?team={team_id}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            if 'response' not in data or not data['response']:
                return Response({"error": "No transfer data found for this team."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare to collect transfer instances
            transfers_to_create = []

            # Process each player's transfer data
            for player_data in data['response']:
                player_id = player_data['player']['id']
                player_name = player_data['player']['name']
                
                # Check if the player exists in the Player model
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    # If player does not exist, fetch and save player data
                    PlayerProfileView().get_player_from_api(player_id)

                # Ensure player_instance is valid before proceeding
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    return Response({"error": f"Player with ID {player_id} could not be created."}, status=status.HTTP_400_BAD_REQUEST)

                # Process each transfer for the player
                for transfer in player_data['transfers']:
                    # Convert the date format from "010712" to "2012-07-01"
                    transfer_date_str = transfer['date']
                    if len(transfer_date_str) == 6:  # Check if the date is in the format "DDMMYY"
                        transfer_date = datetime.strptime(transfer_date_str, "%d%m%y").date()
                    else:
                        transfer_date = datetime.strptime(transfer_date_str, "%Y-%m-%d").date()

                    transfer_type = transfer.get('type', None)
                    team_in_data = transfer['teams']['in']
                    team_out_data = transfer['teams'].get('out', None)  # Use .get() to avoid KeyError

                    # Check if the incoming team exists
                    team_in_instance = Team.objects.filter(team_id=team_in_data['id']).first()
                    if not team_in_instance:
                        print(f"Incoming team with ID {team_in_data['id']} not found. Fetching from API.")
                        TeamIDView().fetch_team_from_api(team_in_data['id'])
                        team_in_instance = Team.objects.filter(team_id=team_in_data['id']).first()
                        if not team_in_instance:
                            print(f"Failed to find incoming team after fetching: {team_in_data['id']}")
                            continue  # Skip this transfer if the team is still not found

                    # Check if the outgoing team exists
                    if team_out_data:  # Only proceed if team_out_data is not None
                        team_out_instance = Team.objects.filter(team_id=team_out_data['id']).first()
                        if not team_out_instance:
                            print(f"Outgoing team with ID {team_out_data['id']} not found. Fetching from API.")
                            TeamIDView().fetch_team_from_api(team_out_data['id'])
                            team_out_instance = Team.objects.filter(team_id=team_out_data['id']).first()
                            if not team_out_instance:
                                print(f"Failed to find outgoing team after fetching: {team_out_data['id']}")
                                continue  # Skip this transfer if the team is still not found

                        # Check if both teams are now available
                        if team_in_instance and team_out_instance:
                            # Prepare the Transfer instance for bulk creation
                            transfers_to_create.append(
                                Transfer(
                                    player=player_instance,
                                    team_in=team_in_instance,
                                    team_out=team_out_instance,
                                    transfer_date=transfer_date,
                                    transfer_type=transfer_type
                                )
                            )
                        else:
                            print(f"Cannot create transfer for player {player_name}: Missing team data.")
                    else:
                        # Handle the case where there is no outgoing team
                        print(f"No outgoing team data for player {player_name}.")
                        continue  # Skip this transfer if there's no outgoing team

            # Bulk create all transfers at once
            if transfers_to_create:
                Transfer.objects.bulk_create(transfers_to_create)
                return Response({"message": "Transfers saved successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "No transfers to save."}, status=status.HTTP_204_NO_CONTENT)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch transfer data: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TransfersTeamOutView(APIView):
    def get(self, request, team_id):
        # Filter transfers where team_in matches the provided team_id and exclude transfers with transfer_type "Loan"
        transfers = Transfer.objects.filter(team_out__team_id=team_id).exclude(transfer_type="Loan").order_by('-transfer_date')
        
        if transfers.exists():
            serializer = TransferSerializer(transfers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "No transfers found for this team."}, status=status.HTTP_404_NOT_FOUND)
    


class TransfersTeamLoanInView(APIView):
    def get(self, request, team_id):
        # Filter transfers where team_in matches the provided team_id and transfer_type is "Loan"
        loan_transfers = Transfer.objects.filter(team_in__team_id=team_id, transfer_type="Loan").order_by('-transfer_date')
        
        if loan_transfers.exists():
            serializer = TransferSerializer(loan_transfers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    


class TransfersTeamLoanOutView(APIView):
    def get(self, request, team_id):
        # Filter transfers where team_out matches the provided team_id and transfer_type is "Loan"
        loan_out_transfers = Transfer.objects.filter(team_out__team_id=team_id, transfer_type="Loan").order_by('-transfer_date')
        
        if loan_out_transfers.exists():
            serializer = TransferSerializer(loan_out_transfers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "No loan transfers found for this team."}, status=status.HTTP_404_NOT_FOUND)



class TransfersPlayerView(APIView):

    def get(self, request, player_id):
        # Fetch transfers where the player matches the provided player_id
        transfers = Transfer.objects.filter(player__player_id=player_id).order_by('-transfer_date')
        if transfers.exists():
            serializer = TransferSerializer(transfers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # If not found, fetch from API, save, and return
        return self.get_player_transfers_from_api(player_id)

    def get_player_transfers_from_api(self, player_id):
        url = f'https://v3.football.api-sports.io/transfers?player={player_id}'
        headers = accheaders
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if 'response' not in data or not data['response']:
                return Response({"error": "No transfer data found for this player."}, status=status.HTTP_404_NOT_FOUND)

            transfers_to_create = []

            for player_data in data['response']:
                player_id = player_data['player']['id']
                player_name = player_data['player']['name']
                
                player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    PlayerProfileView().get_player_from_api(player_id)
                    player_instance = Player.objects.filter(player_id=player_id).first()
                if not player_instance:
                    continue

                for transfer in player_data['transfers']:
                    transfer_date_str = transfer['date']
                    if len(transfer_date_str) == 6:
                        transfer_date = datetime.strptime(transfer_date_str, "%d%m%y").date()
                    else:
                        transfer_date = datetime.strptime(transfer_date_str, "%Y-%m-%d").date()

                    transfer_type = transfer.get('type', None)
                    team_in_data = transfer['teams']['in']
                    team_out_data = transfer['teams'].get('out', None)

                    team_in_instance = Team.objects.filter(team_id=team_in_data['id']).first()
                    if not team_in_instance:
                        TeamIDView().fetch_team_from_api(team_in_data['id'])
                        team_in_instance = Team.objects.filter(team_id=team_in_data['id']).first()
                    if not team_in_instance:
                        continue

                    if team_out_data:
                        team_out_instance = Team.objects.filter(team_id=team_out_data['id']).first()
                        if not team_out_instance:
                            TeamIDView().fetch_team_from_api(team_out_data['id'])
                            team_out_instance = Team.objects.filter(team_id=team_out_data['id']).first()
                        if not team_out_instance:
                            continue

                        transfers_to_create.append(
                            Transfer(
                                player=player_instance,
                                team_in=team_in_instance,
                                team_out=team_out_instance,
                                transfer_date=transfer_date,
                                transfer_type=transfer_type
                            )
                        )
                    else:
                        continue

            if transfers_to_create:
                Transfer.objects.bulk_create(transfers_to_create)

            # Return all transfers for this player after saving
            transfers = Transfer.objects.filter(player__player_id=player_id).order_by('-transfer_date')
            serializer = TransferSerializer(transfers, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED if transfers_to_create else status.HTTP_204_NO_CONTENT)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to fetch transfer data: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)