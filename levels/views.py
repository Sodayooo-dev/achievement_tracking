from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from levels.models import Levels
from levels.serializers import LevelsSerializer


# Create your views here.
class LevelsListCreate(APIView):
    def get(self,request):
        levels = Levels.objects.all()
        serializer = LevelsSerializer(levels, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = LevelsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )