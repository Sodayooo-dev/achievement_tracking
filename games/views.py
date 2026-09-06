from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from games.models import Games
from games.serializers import GameSerializer


# Create your views here.
class GamesListCreate(APIView):
    def get(self,request):
        games = Games.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )