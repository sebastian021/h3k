from rest_framework import serializers
from .models import TeamInformation, TeamStatistics, PlayersInformation


class TeamInformationSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeamInformation
        fields = '__all__'

class TeamStatisticSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeamStatistics
        fields = '__all__'

class PlayersInformationSerializers(serializers.ModelSerializer):
    class Meta:
        model = PlayersInformation
        fields = '__all__'