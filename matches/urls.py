from django.urls import path
from .views import MatchesAPIView, MatchStatisticsView, MatchEventsView

urlpatterns = [
    path('<str:date>/', MatchesAPIView.as_view(), name='matches_api'),
    path('statistics/<int:fixture_id>/', MatchStatisticsView.as_view(), name='matches_statistics'),
    path('events/<int:fixture_id>/', MatchEventsView.as_view(), name='fixture_statistics'),
]