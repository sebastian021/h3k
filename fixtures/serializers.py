from rest_framework import serializers
from .models import Fixtures, FixtureStats, FixturesEvents, FixturesLineUps, FixturesPlayerStats

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

class FixturesPlayerStatSerializers(serializers.ModelSerializer):
    class Meta:
        model = FixturesPlayerStats
        fields = '__all__'       