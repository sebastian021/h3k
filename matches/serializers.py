from rest_framework import serializers 
from .models import Match, MatchStats

class MatchSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Match 
        fields = '__all__' 

class MatchStatsSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = MatchStats 
        fields = '__all__' 