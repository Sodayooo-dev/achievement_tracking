from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from player_games.models import PlayerGames
from player_games.serializers import PlayerGamesSerializer
from player_profiles.permissions import IsAdmin


class PlayerGamesList(APIView):
    def get(self, request):
        games = PlayerGames.objects.all()
        serializer = PlayerGamesSerializer(games, many=True)
        return Response(serializer.data)

class PlayerGamesCreate(APIView):
    permission_classes = [IsAdmin]
    def post(self, request):
        serializer = PlayerGamesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PlayerGamesDetail(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        try:
            game = PlayerGames.objects.get(pk=pk)
        except PlayerGames.DoesNotExist:
            return None

class PlayerGamesUpdate(APIView):
    permission_classes = [IsAdmin]
    def put(self, request, pk):
        try:
            game = PlayerGames.objects.get(pk=pk)
        except PlayerGames.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PlayerGamesSerializer(game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PlayerGamesDelete(APIView):
    permission_classes = [IsAdmin]
    def delete(self, request, pk):
        try:
            game = PlayerGames.objects.get(pk=pk)
        except PlayerGames.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)