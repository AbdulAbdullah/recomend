from django.contrib import admin
from .models import Bottle, UserRecommendation

@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'region', 'style', 'price', 'age')
    search_fields = ('name', 'brand', 'region', 'style')
    list_filter = ('region', 'style', 'country')

@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('username', 'bottle', 'score', 'created_at')
    search_fields = ('username', 'bottle__name')
    list_filter = ('created_at',)