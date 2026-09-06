from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from player_games.models import PlayerGames
from player_games.serializers import PlayerGamesSerializer


class PlayerGamesListCreate(APIView):
    def get(self, request):
        games = PlayerGames.objects.all()
        serializer = PlayerGamesSerializer(games, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlayerGamesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )