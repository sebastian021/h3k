from rest_framework import serializers
from .models import Fixtures, FixtureStats, FixturesEvents, FixturesLineUps

class FixturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixtures
        fields = '__all__'


class FixtureStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixtureStats
        fields = '__all__'

class FixturesEventsSerializers(serializers.ModelSerializer):
    class Meta:
        model = FixturesEvents
        fields = '__all__'


class FixturesLineUpSerializers(serializers.ModelSerializer):
    class Meta:
        model = FixturesLineUps
        fields = '__all__'