from django.urls import path
from .views import LeagueView, TeamView, CoachView, PlayerView, FixtureView, FixtureRoundView, FixtureStatView, FixtureEventView, FixtureLineupView, FixturePlayerView


urlpatterns = [
    path('<str:league>', LeagueView.as_view(), name='league_data'),
    path('<str:league>/teams/<int:season>', TeamView.as_view(), name='teams'),
    path('<str:league>/teams', TeamView.as_view(), name='teams'),
    path('teams/<int:team_id>/coaches', CoachView.as_view(), name='coach'),
    path('<str:league>/teams/<int:team_id>/players', PlayerView.as_view(), name='player'),
    path('<str:league>/teams/<int:team_id>/<int:season>/players', PlayerView.as_view(), name='season_player'),
    path('<str:league>/fixtures/<int:season>', FixtureView.as_view(), name='all_fixtures_by_year'),
    path('<str:league>/fixtures', FixtureView.as_view(), name='all_fixtures'),
    path('<str:league>/fixtures/round/<int:league_round>', FixtureRoundView.as_view(), name='fixture_by_round'), 
    path('<str:league>/fixtures/<int:season>/round/<int:league_round>', FixtureRoundView.as_view(), name='fixture_by_season_and_round'),
    path('fixtures/stats/<int:fixture_id>', FixtureStatView.as_view(), name='fixture_stats'),
    path('fixtures/events/<int:fixture_id>', FixtureEventView.as_view(), name='events'),
    path('fixtures/lineup/<int:fixture_id>', FixtureLineupView.as_view(), name='lineup'),
    path('fixtures/players/<int:fixture_id>', FixturePlayerView.as_view(), name='fixture_player'),
    
    ]