from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Bottle, UserRecommendation
from .serializers import (
    BottleSerializer, 
    UserRecommendationSerializer,
    RecommendationRequestSerializer,
    RecommendationResponseSerializer
)

from recommendation_engine.recommender import WhiskyRecommender
from data_integration.baxus_api import BaxusAPI

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class HealthCheckView(APIView):
    """
    A simple health check endpoint to verify the API is running.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Check if the API is running")
    def get(self, request):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)


class BottleListView(generics.ListAPIView):
    """
    List all available bottles with optional filters like region, style, price, and age.
    """
    queryset = Bottle.objects.all()
    serializer_class = BottleSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of bottles with optional filters.",
        manual_parameters=[
            openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region", type=openapi.TYPE_STRING),
            openapi.Parameter('style', openapi.IN_QUERY, description="Filter by style", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('min_age', openapi.IN_QUERY, description="Minimum age", type=openapi.TYPE_INTEGER),
        ]
    )
    def get_queryset(self):
        queryset = Bottle.objects.all()

        region = self.request.query_params.get('region')
        style = self.request.query_params.get('style')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_age = self.request.query_params.get('min_age')

        if region:
            queryset = queryset.filter(region=region)
        if style:
            queryset = queryset.filter(style=style)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if min_age:
            queryset = queryset.filter(age__gte=min_age)

        return queryset


class UserBarView(APIView):
    """
    Retrieve a user's bar inventory from the external BAXUS API.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a user's bar from BAXUS using their username.",
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_PATH, description="User's username", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, username):
        try:
            baxus_api = BaxusAPI()
            user_bar = baxus_api.get_user_bar(username)
            return Response(user_bar, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve user's bar: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendationView(APIView):
    """
    Generate whisky recommendations based on a user's preferences and return their recommendation history.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RecommendationRequestSerializer,
        responses={200: openapi.Response('List of recommendations', BottleSerializer(many=True))},
        operation_description="Generate whisky recommendations for a user."
    )
    def post(self, request):
        serializer = RecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        count = serializer.validated_data.get('count', 5)
        include_reasoning = serializer.validated_data.get('include_reasoning', True)

        try:
            recommender = WhiskyRecommender()
            recommendations = recommender.get_recommendations(
                username=username,
                count=count,
                include_reasoning=include_reasoning
            )

            # Validate recommendations with the response serializer
            response_serializer = RecommendationResponseSerializer(data=recommendations, many=True)
            if response_serializer.is_valid():
                # Create UserRecommendation records
                for rec in recommendations:
                    try:
                        bottle = Bottle.objects.get(bottle_id=rec['bottle_id'])
                        UserRecommendation.objects.create(
                            username=username,
                            bottle=bottle,
                            score=rec['score'],
                            reason=rec.get('reason', '')
                        )
                    except Bottle.DoesNotExist:
                        continue

                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid recommendation format", "details": response_serializer.errors},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {"error": f"Failed to generate recommendations: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Username to get recommendations for", type=openapi.TYPE_STRING),
        ],
        responses={200: UserRecommendationSerializer(many=True)},
        operation_description="Retrieve a user's past whisky recommendations."
    )
    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response(
                {"error": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        recommendations = UserRecommendation.objects.filter(
            username=username
        ).order_by('-created_at')

        serializer = UserRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
