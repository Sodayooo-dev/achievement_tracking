from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from levels.models import Levels
from levels.serializers import LevelsSerializer
from player_profiles.permissions import IsAdmin


class LevelsList(APIView):
    def get(self, request):
        levels = Levels.objects.all()
        serializer = LevelsSerializer(levels, many=True)
        return Response(serializer.data)

class LevelsCreate(APIView):
    permission_classes = [IsAdmin]
    def post(self, request):
        serializer = LevelsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LevelsDetail(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        try:
            level = Levels.objects.get(pk=pk)
        except Levels.DoesNotExist:
            return Response(
                data={'message': 'Level does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = LevelsSerializer(level)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LevelsUpdate(APIView):
    permission_classes = [IsAdmin]
    def put(self, request, pk):
        try:
            level = Levels.objects.get(pk=pk)
        except Levels.DoesNotExist:
            return Response(
                data={'message': 'Level does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = LevelsSerializer(level, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LevelsDelete(APIView):
    permission_classes = [IsAdmin]
    def delete(self, request, pk):
        try:
            level = Levels.objects.get(pk=pk)
        except Levels.DoesNotExist:
            return Response(
                data={'message': 'Level does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        level.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)