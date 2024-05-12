from django.urls import path
from .views import MatchesAPIView, MatchStatisticsView

urlpatterns = [
    path('<str:date>/', MatchesAPIView.as_view(), name='matches_api'),
    path('statistics/<int:fixture_id>/', MatchStatisticsView.as_view(), name='matches_statistics'),
]