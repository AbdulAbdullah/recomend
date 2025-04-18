from rest_framework import serializers
from .models import Bottle, UserRecommendation

class BottleSerializer(serializers.ModelSerializer):
    bottle_id = serializers.CharField(read_only=True)  # Add this line
    
    class Meta:
        model = Bottle
        fields = ('bottle_id', 'name', 'brand', 'region', 'style', 'price', 'age', 'abv', 'flavor_profile', 'description')

class UserRecommendationSerializer(serializers.ModelSerializer):
    bottle = BottleSerializer(read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = ('id', 'username', 'bottle', 'score', 'reason', 'created_at')

class RecommendationResponseSerializer(serializers.Serializer):
    bottle_id = serializers.CharField()
    name = serializers.CharField()
    brand = serializers.CharField(allow_blank=True)
    region = serializers.CharField(allow_blank=True)
    style = serializers.CharField(allow_blank=True)
    price = serializers.FloatField()
    age = serializers.IntegerField(allow_null=True)
    score = serializers.FloatField()
    abv = serializers.FloatField(allow_null=True)
    flavor_profile = serializers.DictField(allow_empty=True)
    description = serializers.CharField(allow_blank=True)
    reason = serializers.CharField(allow_blank=True, required=False)

class RecommendationRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    count = serializers.IntegerField(required=False, default=5)
    include_reasoning = serializers.BooleanField(required=False, default=True)