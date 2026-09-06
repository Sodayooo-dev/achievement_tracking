from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from player_achievements.models import PlayerAchievements
from player_achievements.serializers import PlayerAchievementsSerializer


class PlayerAchievementsListCreate(APIView):
    def get(self,request):
        achievements = PlayerAchievements.objects.all()
        serializer = PlayerAchievementsSerializer(achievements, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = PlayerAchievementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )