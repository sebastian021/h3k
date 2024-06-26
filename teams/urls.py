from django.urls import path
from .views import TeamsView, TeamInformationView, TeamStatisticView, PlayersView

urlpatterns = [
    path('<int:season>', TeamsView.as_view(), name='teams'),
    path('', TeamsView.as_view(), name='teamspyth'),
    path('<int:season>/info', TeamInformationView.as_view(), name='team_info'),
    path('info', TeamInformationView.as_view(), name='team_info'),
    path('statistic/<int:season>/<int:team_id>', TeamStatisticView.as_view(), name='team_stats'),
    path('statistic/<int:team_id>', TeamStatisticView.as_view(), name='team_stats_current_season'),
    path('<int:season>/<int:team_id>/players', PlayersView.as_view(), name='player'),
    path('<int:team_id>/players', PlayersView.as_view(), name='teams_player'),
]