from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from player_profiles.permissions import IsAdmin
from roles.models import Roles
from roles.serializers import RoleSerializer


class RolesList(APIView):
    def get(self, request, format=None):
        roles = Roles.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

class RolesCreate(APIView):
    permission_classes = [IsAdmin]
    def post(self, request, format=None):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class RolesDetail(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, format=None):
        try:
            roles = Roles.objects.all()
        except Roles.DoesNotExist:
            return None

class RolesUpdate(APIView):
    permission_classes = [IsAdmin]
    def put(self, request, format=None):
        try:
            roles = Roles.objects.all()
        except Roles.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(roles, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class RolesDelete(APIView):
    permission_classes = [IsAdmin]
    def delete(self, request, format=None):
        try:
            roles = Roles.objects.all()
        except Roles.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        roles.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
