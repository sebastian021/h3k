from rest_framework import serializers
from .models import Teams, TeamInformation, TeamStatistics, PlayersInformation

class TeamsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = '__all__'
class TeamInformationSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeamInformation
        fields = ['team', 'team_code', 'team_country', 'team_founded', 'team_national', 'venue']
class TeamStatisticSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeamStatistics
        fields = '__all__'

class PlayersInformationSerializers(serializers.ModelSerializer):
    class Meta:
        model = PlayersInformation
        fields = '__all__'