from rest_framework import serializers 
from .models import Match, MatchStats, MatchesEvents, MatchesLineUps

class MatchSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Match 
        fields = '__all__' 

class MatchStatsSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = MatchStats 
        fields = '__all__' 

class MatchEventsSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = MatchesEvents 
        fields = '__all__' 

class MatchesLineUpSerializers(serializers.ModelSerializer):
    class Meta:
        model = MatchesLineUps
        fields = '__all__'