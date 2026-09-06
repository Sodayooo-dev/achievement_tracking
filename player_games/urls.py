from django.urls import path

from player_games.views import PlayerGamesListCreate

urlpatterns = [
    path('player_games/', PlayerGamesListCreate.as_view())
]