from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.models import Achievements
from achievements.serializers import AchievementsSerializer


class AchievementsListCreate(APIView):
    def get(self,request):
        achievements = Achievements.objects.all()
        serializer = AchievementsSerializer(achievements, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = AchievementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )