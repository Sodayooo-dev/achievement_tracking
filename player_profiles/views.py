from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from player_profiles.serializers import PlayerProfileSerializer


class PlayerProfileLogin(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                data = {'message': 'Please provide both username and password'},
                status = status.HTTP_400_BAD_REQUEST
            )

        profile = authenticate(username=username, password=password)
        if profile is None:
            return Response(
                data = {'message': 'Username or password is invalid'},
                status = status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(profile)
        serializer = PlayerProfileSerializer(profile)
        return Response(
            data = {
                'message': 'Successfully logged in',
                'profile': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            status = status.HTTP_200_OK
        )

class PlayerProfileRegister(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PlayerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data = serializer.data,
                status = status.HTTP_201_CREATED
            )
        return Response(
            data = serializer.errors,
            status = status.HTTP_400_BAD_REQUEST
        )
