from rest_framework import serializers
from .models import Fixtures

class FixturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixtures
        fields = '__all__'
