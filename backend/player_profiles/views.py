from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from player_profiles.models import PlayerProfiles
from player_profiles.permissions import IsAdmin
from player_profiles.serializers import PlayerProfileSerializer, RegistrationSerializer, SelfProfileSerializer
from config.api import ResourceList, ResourceDetail, ResourceUpdate, ResourceDelete


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
        serializer = RegistrationSerializer(data=request.data)
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

class ProfileConfiguration:
    model = PlayerProfiles
    serializer_class = PlayerProfileSerializer
    search_fields = ('username', 'first_name', 'last_name', 'email')


class PlayerProfileList(ProfileConfiguration, ResourceList):
    permission_classes = [IsAdmin]


class PlayerProfileDetail(ProfileConfiguration, ResourceDetail):
    pass


class PlayerProfileUpdate(ProfileConfiguration, ResourceUpdate):
    pass


class PlayerProfileDelete(ProfileConfiguration, ResourceDelete):
    def delete(self, request, pk):
        if request.user.pk == pk:
            return Response({'message': 'You cannot delete your signed-in administrator account.'}, status=409)
        return super().delete(request, pk)


class CurrentProfile(APIView):
    def get(self, request):
        return Response(PlayerProfileSerializer(request.user).data)

    def put(self, request):
        serializer = SelfProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

