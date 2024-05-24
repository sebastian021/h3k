from django.urls import path
from .views import TeamInformationView, TeamStatisticView

urlpatterns = [
    path('<int:season>', TeamInformationView.as_view(), name='team_info'),
    path('', TeamInformationView.as_view(), name='team_info'),
    path('statistic/<int:season>/<int:team_id>', TeamStatisticView.as_view(), name='team_stats'),
    path('statistic/<int:team_id>', TeamStatisticView.as_view(), name='team_stats_current_season')
]