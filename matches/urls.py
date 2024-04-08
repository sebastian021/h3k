from django.urls import path
from . import views

urlpatterns = [
    path('<str:date>/', views.get_matches),
    # Other URL patterns...
]