from rest_framework import serializers
from player_games.models import PlayerGames


class PlayerGamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerGames
        fields = '__all__'