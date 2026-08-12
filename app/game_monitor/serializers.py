# ruff: noqa: TRY003
from typing import ClassVar

from rest_framework import serializers

from .models import Game, UserPhone


class GameSerializer(serializers.ModelSerializer):
    """Serializer for Game model with detailed field descriptions."""
    
    class Meta:
        model = Game
        fields: ClassVar[list[str]] = [
            'id', 'title', 'date', 'home_team', 'away_team',
            'home_team_score', 'away_team_score', 'game_clock', 'period'
        ]
        read_only_fields: ClassVar[list[str]] = ['id']
    
    def validate_home_team_score(self, value):
        """Validate that home team score is non-negative."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Score cannot be negative")
        return value
    
    def validate_away_team_score(self, value):
        """Validate that away team score is non-negative."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Score cannot be negative")
        return value


class UserPhoneSerializer(serializers.ModelSerializer):
    """Serializer for UserPhone model with phone number validation."""
    
    class Meta:
        model = UserPhone
        fields: ClassVar[list[str]] = ['id', 'phone_number']
        read_only_fields: ClassVar[list[str]] = ['id']
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not value:
            raise serializers.ValidationError("Phone number required")
        
        # Remove any spaces or special characters except +
        cleaned_number = value.strip()
        
        # Basic validation - should start with + and contain digits
        if not cleaned_number.startswith('+'):
            raise serializers.ValidationError("Must start with +")
        
        # Check if it contains only digits after the +
        if not cleaned_number[1:].isdigit():
            raise serializers.ValidationError("Must contain only digits after +")
        
        # Check reasonable length (10-15 digits after +)
        if len(cleaned_number[1:]) < 10 or len(cleaned_number[1:]) > 15:
            raise serializers.ValidationError("Must be 10-15 digits")
        
        return cleaned_number


class GameListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for game list views."""
    
    class Meta:
        model = Game
        fields: ClassVar[list[str]] = ['id', 'title', 'home_team', 'away_team', 'date']
        read_only_fields: ClassVar[list[str]] = ['id']