from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from player_achievements.models import PlayerAchievements
from player_achievements.serializers import PlayerAchievementsSerializer
from player_profiles.permissions import IsAdmin


class PlayerAchievementsList(APIView):
    def get(self,request):
        achievements = PlayerAchievements.objects.all()
        serializer = PlayerAchievementsSerializer(achievements, many=True)
        return Response(serializer.data)

class PlayerAchievementsCreate(APIView):
    permission_classes = [IsAdmin]
    def post(self,request):
        serializer = PlayerAchievementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PlayerAchievementsDetail(APIView):
    permission_classes = [IsAdmin]
    def get(self,request,pk):
        try:
            achievements = PlayerAchievements.objects.get(pk=pk)
        except PlayerAchievements.DoesNotExist:
            return None

class PlayerAchievementsUpdate(APIView):
    permission_classes = [IsAdmin]
    def put(self,request,pk):
        try:
            achievements = PlayerAchievements.objects.get(pk=pk)
        except PlayerAchievements.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PlayerAchievementsSerializer(achievements, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PlayerAchievementsDelete(APIView):
    permission_classes = [IsAdmin]
    def delete(self,request,pk):
        try:
            achievements = PlayerAchievements.objects.get(pk=pk)
        except PlayerAchievements.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        achievements.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)