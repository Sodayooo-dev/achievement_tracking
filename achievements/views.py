from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.models import Achievements
from achievements.serializers import AchievementsSerializer
from player_profiles.permissions import IsAdmin


class AchievementsList(APIView):
    def get(self,request):
        achievements = Achievements.objects.all()
        serializer = AchievementsSerializer(achievements, many=True)
        return Response(serializer.data)

class AchievementsCreate(APIView):
    permission_classes = [IsAdmin]
    def post(self,request):
        serializer = AchievementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class AchievementsDetail(APIView):
    permission_classes = [IsAdmin]
    def get(self,request,pk):
        try:
            achievement = Achievements.objects.get(pk=pk)
        except Achievements.DoesNotExist:
            return None