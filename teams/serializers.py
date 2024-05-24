from rest_framework import serializers
from .models import TeamInformation, TeamStatistics


class TeamInformationSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeamInformation
        fields = '__all__'

class TeamStatisticSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeamStatistics
        fields = '__all__'