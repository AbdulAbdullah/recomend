from django.urls import path
from .views import (
    RecommendationView, 
    BottleListView,
    UserBarView,
    HealthCheckView
)

urlpatterns = [
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('bottles/', BottleListView.as_view(), name='bottles'),
    path('user-bar/<str:username>/', UserBarView.as_view(), name='user-bar'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]