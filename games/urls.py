from django.urls import path

from games.views import GamesList, GamesDetail, GamesCreate

urlpatterns = [
    path('games/', GamesList.as_view()),
    path('games/<int:pk>/', GamesDetail.as_view()),
    path('games/new/', GamesCreate.as_view()),
]