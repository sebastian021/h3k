from rest_framework import serializers
from .models import Fixtures, FixtureStats

class FixturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixtures
        fields = '__all__'


class FixtureStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixtureStats
        fields = '__all__'