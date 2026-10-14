from django.db import transaction
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from games.models import Games
from player_games.models import PlayerGames
from player_games.serializers import PlayerGamesSerializer


class LibraryAddition(serializers.Serializer):
    game_id = serializers.PrimaryKeyRelatedField(queryset=Games.objects.all())

    def validate(self, attrs):
        if set(self.initial_data) - {'game_id'}:
            raise serializers.ValidationError('Only game_id is accepted; the server selects the current player.')
        return attrs


class MyLibrary(APIView):
    def post(self, request):
        serializer = LibraryAddition(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            row, created = PlayerGames.objects.get_or_create(player_id=request.user, game_id=serializer.validated_data['game_id'])
        return Response(PlayerGamesSerializer(row).data, status=201 if created else 200)
