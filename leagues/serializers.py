from rest_framework import serializers
from .models import Leagues

class LeagueSerializers(serializers.ModelSerializer):
    class Meta:
        model = Leagues
        fields = '__all__'