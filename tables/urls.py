from django.urls import path
from .views import StandingView

urlpatterns = [
    path('<str:league_name>', StandingView.as_view()),
    path('<str:league_name>/<int:season>', StandingView.as_view()),
]