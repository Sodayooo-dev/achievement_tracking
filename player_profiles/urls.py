from player_profiles.views import PlayerProfileLogin, PlayerProfileRegister
from django.urls import path

urlpatterns = [
    path('login/', PlayerProfileLogin.as_view()),
    path('register/', PlayerProfileRegister.as_view()),
]