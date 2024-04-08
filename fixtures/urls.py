from django.urls import path
from .views import FixturesView

urlpatterns = [
    path('<str:league_name>/', FixturesView.as_view(), name='fixtures'),
]
