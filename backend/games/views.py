from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from games.models import Games
from games.serializers import GameSerializer
from player_profiles.permissions import IsAdmin


# Create your views here.
class GamesList(APIView):
    def get(self,request):
        games = Games.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

class GamesCreate(APIView):
    permission_classes = [IsAdmin]
    def post(self,request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class GamesDetail(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        try:
            game = Games.objects.get(pk=pk)
        except Games.DoesNotExist:
            return Response(
                data={'message': 'Game does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = GameSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GamesUpdate(APIView):
    permission_classes = [IsAdmin]
    def put(self,request,pk):
        try:
            game = Games.objects.get(pk=pk)
        except Games.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = GameSerializer(game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class GamesDelete(APIView):
    permission_classes = [IsAdmin]
    def delete(self,request,pk):
        try:
            game = Games.objects.get(pk=pk)
        except Games.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)