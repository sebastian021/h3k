from django.urls import path
from .views import LeaguesView

urlpatterns = [
    path('<str:league>', LeaguesView.as_view(), name='teams_list'),
]