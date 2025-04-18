from rest_framework import serializers
from .models import Bottle, UserRecommendation

class BottleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bottle
        fields = '__all__'

class UserRecommendationSerializer(serializers.ModelSerializer):
    bottle = BottleSerializer(read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = ('id', 'username', 'bottle', 'score', 'reason', 'created_at')

class RecommendationRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    count = serializers.IntegerField(required=False, default=5)
    include_reasoning = serializers.BooleanField(required=False, default=True)