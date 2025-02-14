from django.urls import path, re_path
from .views import LeagueListView, LeagueView, TeamView, TeamStatView, CoachView, PlayerView, FixtureView, FixtureRoundView, FixtureRoundFaView, FixtureDateView, FixtureStatView, FixtureEventView, FixtureLineupView, FixturePlayerView, FixtureH2H, TableView


urlpatterns = [
    path('SupportedLeagues', LeagueListView.as_view(), name='league_list'),
    path('<str:league>', LeagueView.as_view(), name='league_data'),
    path('teams/<str:league>', TeamView.as_view(), name='teams'),
    path('teams/<str:league>/<int:season>', TeamView.as_view(), name='teams'),
    path('team-stat/<str:league>/<int:team_id>/<int:season>/', TeamStatView.as_view(), name='team-stat'),
    path('team-stat/<int:league>/<int:team_id>', TeamStatView.as_view(), name='team-stat'),
    path('coaches/team/<int:team_id>', CoachView.as_view(), name='coach'),
    path('players/<str:league>/<int:team_id>', PlayerView.as_view(), name='player-list'),
    path('players/<str:league>/<int:team_id>/<int:season>', PlayerView.as_view(), name='player-list-season'),
    path('fixtures/<str:league>/<int:season>', FixtureView.as_view(), name='all_fixtures_by_year'),
    path('fixtures/<str:league>/', FixtureView.as_view(), name='all_fixtures'),
    path('fixtures/<str:league>/<str:season>/<str:fixture_round>/', FixtureRoundView.as_view(), name='fixture-rounds'),
    path('fixtures/<str:league>/<str:fixture_round>/', FixtureRoundView.as_view(), name='fixture-rounds'),
    
    re_path(
        r'^fixtures/fa/(?P<league>[\w-]+)/(?P<season>\d{4})/(?P<fixture_round_fa>.+)$', 
        FixtureRoundFaView.as_view(), 
        name='fixture-round-fa'
    ),

    re_path(
        r'^fixtures/fa/(?P<league>[\w-]+)/(?P<fixture_round_fa>.+)$', 
        FixtureRoundFaView.as_view(), 
        name='fixture-round-fa'
    ),    



    path('fixtures/stats/match/<int:fixture_id>', FixtureStatView.as_view(), name='fixture_stats'),
    path('fixtures/events/match/<int:fixture_id>', FixtureEventView.as_view(), name='events'),
    path('fixtures/lineup/match/<int:fixture_id>', FixtureLineupView.as_view(), name='lineup'),
    path('fixtures/players/match/<int:fixture_id>', FixturePlayerView.as_view(), name='fixture_player'),
    path('fixtures/h2h/match/<int:fixture_id>', FixtureH2H.as_view(), name='head_to_head'),
    path('fixtures/date', FixtureDateView.as_view(), name='fixture-date'),
    path('fixtures/date/<str:date>', FixtureDateView.as_view(), name='fixture-date-with-date'),
    path('tables/<str:league>/<str:season>', TableView.as_view(), name='table_by_season'),
    path('tables/<str:league>', TableView.as_view(), name='current_table'),
    ]