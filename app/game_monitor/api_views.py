from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Game, UserPhone
from .nba import get_scoreboard as get_nba_scoreboard
from .serializers import GameListSerializer, GameSerializer, UserPhoneSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all games",
        description="Retrieve a paginated list of all NBA/WNBA games in the database",
        responses={200: GameListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get a specific game",
        description="Retrieve detailed information about a specific game by ID",
        responses={200: GameSerializer},
    ),
    create=extend_schema(
        summary="Create a new game",
        description="Add a new game to the database (admin function)",
        request=GameSerializer,
        responses={201: GameSerializer},
    ),
    update=extend_schema(
        summary="Update a game",
        description="Update an existing game's information",
        request=GameSerializer,
        responses={200: GameSerializer},
    ),
    destroy=extend_schema(
        summary="Delete a game",
        description="Remove a game from the database",
        responses={204: None},
    ),
)
class GameViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing NBA/WNBA games.
    
    Provides CRUD operations for game data including:
    - List all games
    - Get specific game details
    - Create/update/delete games (admin functions)
    - Fetch live game data from NBA API
    """
    queryset = Game.objects.all().order_by('-date')
    serializer_class = GameSerializer
    
    def get_serializer_class(self):
        """Use lightweight serializer for list views."""
        if self.action == 'list':
            return GameListSerializer
        return GameSerializer
    
    @extend_schema(
        summary="Fetch live NBA games",
        description="Fetch current NBA and WNBA games from the official API and update the database",
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Success Response",
                value={"status": "success", "games_updated": 5, "message": "Games updated successfully"}
            ),
            OpenApiExample(
                "Error Response",
                value={"status": "error", "message": "Unable to fetch games"}
            )
        ]
    )
    @action(detail=False, methods=['post'])
    def fetch_live_games(self, request):
        """
        Fetch live games from NBA API and update the database.
        
        This endpoint calls the NBA scoreboard API to get current game data
        and updates the local database with the latest information.
        """
        try:
            data = get_nba_scoreboard()
            
            if not data or 'games' not in data:
                return Response(
                    {"status": "error", "message": "Unable to fetch games or invalid data format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            games_count = 0
            for game_data in data.get('games', []):
                # Update or create game based on title
                Game.objects.update_or_create(
                    title=game_data.get('title', ''),
                    defaults={
                        'home_team': game_data.get('home_team', ''),
                        'away_team': game_data.get('away_team', ''),
                        'home_team_score': game_data.get('home_team_score'),
                        'away_team_score': game_data.get('away_team_score'),
                        'game_clock': game_data.get('game_clock', ''),
                        'period': game_data.get('period'),
                    }
                )
                games_count += 1
            
            return Response({
                "status": "success",
                "games_updated": games_count,
                "message": f"Successfully updated {games_count} games"
            })
            
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get close games",
        description="Retrieve games that are close in score (within 10 points) and in the 4th quarter or later",
        parameters=[
            OpenApiParameter(
                name="point_diff",
                type=OpenApiTypes.INT,
                description="Maximum point difference to consider 'close' (default: 10)",
                required=False,
            ),
            OpenApiParameter(
                name="min_period",
                type=OpenApiTypes.INT,
                description="Minimum period to consider (default: 4)",
                required=False,
            ),
        ],
        responses={200: GameSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def close_games(self, request):
        """
        Get games that are close in score.
        
        Returns games where the point difference is within the specified threshold
        and the game is in the specified period or later (typically 4th quarter+).
        """
        point_diff = int(request.query_params.get('point_diff', 10))
        min_period = int(request.query_params.get('min_period', 4))
        
        close_games = []
        for game in self.queryset:
            if (game.home_team_score is not None and 
                game.away_team_score is not None and
                game.period is not None and
                game.period >= min_period):
                
                score_diff = abs(game.home_team_score - game.away_team_score)
                if score_diff <= point_diff:
                    close_games.append(game)
        
        serializer = self.get_serializer(close_games, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all registered phone numbers",
        description="Retrieve a list of all phone numbers registered for game notifications",
        responses={200: UserPhoneSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get a specific phone number",
        description="Retrieve details about a specific registered phone number",
        responses={200: UserPhoneSerializer},
    ),
    create=extend_schema(
        summary="Register a phone number",
        description="Register a new phone number to receive game notifications",
        request=UserPhoneSerializer,
        responses={201: UserPhoneSerializer},
    ),
    destroy=extend_schema(
        summary="Unregister a phone number",
        description="Remove a phone number from the notification list",
        responses={204: None},
    ),
)
class UserPhoneViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing phone number registrations.
    
    Provides CRUD operations for phone numbers that will receive
    notifications when games are close in the final minutes.
    """
    queryset = UserPhone.objects.all()
    serializer_class = UserPhoneSerializer
    
    def get_serializer_class(self):
        """Use the same serializer for all operations."""
        return UserPhoneSerializer
    
    @extend_schema(
        summary="Validate phone number",
        description="Validate a phone number format without saving it",
        request=OpenApiTypes.STR,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Valid Number",
                value={"valid": True, "phone_number": "+14155552671", "message": "Phone number is valid"}
            ),
            OpenApiExample(
                "Invalid Number",
                value={"valid": False, "phone_number": "123", "message": "Invalid phone number format"}
            )
        ]
    )
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """
        Validate a phone number format without saving it.
        
        Useful for frontend validation before submitting the registration form.
        """
        phone_number = request.data.get('phone_number', '')
        
        if not phone_number:
            return Response(
                {"valid": False, "message": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = self.get_serializer(data={'phone_number': phone_number})
            if serializer.is_valid():
                return Response({
                    "valid": True,
                    "phone_number": serializer.validated_data['phone_number'],
                    "message": "Phone number is valid"
                })
            else:
                return Response({
                    "valid": False,
                    "message": serializer.errors.get('phone_number', ['Invalid phone number'])[0]
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"valid": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )