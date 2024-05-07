from django.urls import path
from .views import FixturesAPIView, FixtureStatistics

urlpatterns = [
    path('<int:year>/<str:league>/<str:round>/', FixturesAPIView.as_view(), name='fixtures_api'),
    path('statistics/<int:fixture_id>/', FixtureStatistics.as_view(), name='fixture_statistics'),
]
