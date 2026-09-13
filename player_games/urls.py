from django.urls import path

from player_games.views import PlayerGamesList, PlayerGamesDetail, PlayerGamesCreate, PlayerGamesUpdate, \
    PlayerGamesDelete

urlpatterns = [
    path('player_games/', PlayerGamesList.as_view()),
    path('player_games/<int:pk>/', PlayerGamesDetail.as_view()),
    path('player_games/new/', PlayerGamesCreate.as_view()),
    path('player_games/<int:pk>/update/', PlayerGamesUpdate.as_view()),
    path('player_games/<int:pk>/delete/', PlayerGamesDelete.as_view())
]