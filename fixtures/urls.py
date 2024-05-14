from django.urls import path
from .views import FixturesAPIView, FixtureStatistics, FixtureEvents, FixturesLineUpView, FixturesPlayersStatsView

urlpatterns = [
    path('<int:year>/<str:league>/<str:round>/', FixturesAPIView.as_view(), name='fixtures_api'),
    path('statistics/<int:fixture_id>/', FixtureStatistics.as_view(), name='fixture_statistics'),
    path('events/<int:fixture_id>/', FixtureEvents.as_view(), name='fixture_events'),
    path('lineup/<int:fixture_id>/', FixturesLineUpView.as_view(), name='fixture_lineup'),
    path('playersStats/<int:fixture_id>/', FixturesPlayersStatsView.as_view(), name='playersStats')

    
]
