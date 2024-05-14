from django.urls import path
from .views import MatchesAPIView, MatchStatisticsView, MatchEventsView, MatchesLineUpView, MatchesPlayersStatsView

urlpatterns = [
    path('<str:date>/', MatchesAPIView.as_view(), name='matches_api'),
    path('statistics/<int:fixture_id>/', MatchStatisticsView.as_view(), name='matches_statistics'),
    path('events/<int:fixture_id>/', MatchEventsView.as_view(), name='match_events'),
    path('lineup/<int:fixture_id>/', MatchesLineUpView.as_view(), name='match_lineup'),
    path('playerStats/<int:fixture_id>/', MatchesPlayersStatsView.as_view(), name='matches_players_stats')
]