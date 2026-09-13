from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.models import Achievements
from levels.models import Levels
from levels.serializers import LevelsSerializer
from player_profiles.permissions import IsAdmin


# Create your views here.
class LevelsList(APIView):
    def get(self,request):
        levels = Levels.objects.all()
        serializer = LevelsSerializer(levels, many=True)
        return Response(serializer.data)

class LevelsCreate(APIView):
    permission_classes = (IsAdmin)
    def post(self,request):
        serializer = LevelsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LevelsDetail(APIView):
    permission_classes = (IsAdmin)
    def get(self,request,pk):
        try:
            achievement = Achievements.objects.get(pk=pk)
        except Achievements.DoesNotExist:
            return None