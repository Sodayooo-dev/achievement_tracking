from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from player_games.models import PlayerGames


class PlayerGamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerGames
        fields = '__all__'
        validators = [UniqueTogetherValidator(queryset=PlayerGames.objects.all(), fields=('player_id', 'game_id'), message='This game is already in the player library.')]
